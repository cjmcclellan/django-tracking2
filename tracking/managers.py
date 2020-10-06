from __future__ import division

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Avg
from django.db.models import Q
import operator
from functools import reduce

from tracking.settings import TRACK_PAGEVIEWS, TRACK_ANONYMOUS_USERS, TRACK_SELECTED_URLS
from tracking.cache import CacheManager
import geoip2.database
import os


class VisitorManager(CacheManager):
    def active(self, registered_only=True):
        "Returns all active users, e.g. not logged and non-expired session."
        visitors = self.filter(
            expiry_time__gt=timezone.now(),
            end_time=None
        )
        if registered_only:
            visitors = visitors.filter(user__isnull=False)
        return visitors

    def registered(self):
        return self.get_queryset().filter(user__isnull=False)

    def guests(self):
        return self.get_queryset().filter(user__isnull=True)

    def stats(self, start_date, end_date, registered_only=False):
        """Returns a dictionary of visits including:

            * total visits
            * unique visits
            * return ratio
            * pages per visit (if pageviews are enabled)
            * time on site

        for all users, registered users and guests.
        """
        visitors = self.filter(
            start_time__gte=start_date,
            start_time__lt=end_date
        )

        stats = {
            'total': 0,
            'unique': 0,
            'return_ratio': 0,
        }

        # All visitors
        stats['total'] = total_count = visitors.count()
        unique_count = 0

        # No visitors! Nothing more to do.
        if not total_count:
            return stats

        # Avg time on site
        total_time_on_site = visitors.aggregate(
            avg_tos=Avg('time_on_site'))['avg_tos']
        stats['time_on_site'] = timedelta(seconds=int(total_time_on_site))

        # Registered user sessions
        registered_visitors = visitors.filter(user__isnull=False)
        registered_total_count = registered_visitors.count()

        if registered_total_count:
            registered_unique_count = registered_visitors.values(
                'user'
            ).distinct().count()
            # Avg time on site
            time_on_site = registered_visitors.aggregate(
                avg_tos=Avg('time_on_site'))['avg_tos']

            # Update the total unique count..
            unique_count += registered_unique_count

            # Set the registered stats..
            returns = (registered_total_count - registered_unique_count)
            stats['registered'] = {
                'total': registered_total_count,
                'unique': registered_unique_count,
                'return_ratio': (returns / registered_total_count) * 100,
                'time_on_site': timedelta(seconds=int(time_on_site)),
            }

        # Get stats for our guests..
        if TRACK_ANONYMOUS_USERS and not registered_only:
            guests = visitors.filter(user__isnull=True)
            guest_total_count = guests.count()

            if guest_total_count:
                guest_unique_count = guests.values(
                    'ip_address'
                ).distinct().count()
                # Avg time on site
                guest_time_on_site = guests.aggregate(
                    avg_tos=Avg('time_on_site'))['avg_tos']
                # return rate
                returns = (guest_total_count - guest_unique_count)
                return_ratio = (returns / guest_total_count) * 100
                time_on_site = timedelta(seconds=int(guest_time_on_site))
            else:
                guest_total_count = 0
                guest_unique_count = 0
                return_ratio = 0.0
                time_on_site = timedelta(0)

            # Update the total unique count
            unique_count += guest_unique_count
            stats['guests'] = {
                'total': guest_total_count,
                'unique': guest_unique_count,
                'return_ratio': return_ratio,
                'time_on_site': time_on_site,
            }

        # Finish setting the total visitor counts
        returns = (total_count - unique_count)
        stats['unique'] = unique_count
        stats['return_ratio'] = (returns / total_count) * 100

        # If pageviews are being tracked, add the aggregate pages-per-visit
        if TRACK_PAGEVIEWS:
            if 'registered' in stats:
                pages_per_visit = registered_visitors.annotate(
                    page_count=Count('pageviews')
                ).filter(page_count__gt=0).aggregate(
                    pages_per_visit=Avg('page_count'))['pages_per_visit']
                stats['registered']['pages_per_visit'] = pages_per_visit

            if TRACK_ANONYMOUS_USERS and not registered_only:
                stats['guests']['pages_per_visit'] = guests.annotate(
                    page_count=Count('pageviews')
                ).filter(page_count__gt=0).aggregate(
                    pages_per_visit=Avg('page_count'))['pages_per_visit']

                total_per_visit = visitors.annotate(
                    page_count=Count('pageviews')
                ).filter(page_count__gt=0).aggregate(
                    pages_per_visit=Avg('page_count'))['pages_per_visit']
            else:
                if 'registered' in stats:
                    total_per_visit = stats['registered']['pages_per_visit']
                else:
                    total_per_visit = 0

            stats['pages_per_visit'] = total_per_visit

        return stats

    def user_stats(self, start_date=None, end_date=None):
        user_kwargs = {
            'visit_history__start_time__lt': end_date,
        }
        visit_kwargs = {
            'start_time__lt': end_date,
        }
        if start_date:
            user_kwargs['visit_history__start_time__gte'] = start_date
            visit_kwargs['start_time__gte'] = start_date
        else:
            user_kwargs['visit_history__start_time__isnull'] = False
            visit_kwargs['start_time__isnull'] = False

        users = list(get_user_model().objects.filter(**user_kwargs).annotate(
            visit_count=Count('visit_history'),
            time_on_site=Avg('visit_history__time_on_site'),
        ).filter(visit_count__gt=0).order_by(
            '-time_on_site',
            get_user_model().USERNAME_FIELD,
        ))

        # Aggregate pageviews per visit
        for user in users:
            user.pages_per_visit = user.visit_history.filter(
                **visit_kwargs
            ).annotate(
                page_count=Count('pageviews')
            ).filter(page_count__gt=0).aggregate(
                pages_per_visit=Avg('page_count'))['pages_per_visit']
            # Lop off the floating point, turn into timedelta
            user.time_on_site = timedelta(seconds=int(user.time_on_site))
        return users


class PageviewManager(models.Manager):
    def stats(self, start_date=None, end_date=None, registered_only=False, filter_agents=None, remove_locations=None):
        """Returns a dictionary of pageviews including:

            * total pageviews

        for all users, registered users and guests.
        """

        # tracker for all the exact locations
        geo_location = {'None': {'lat': None, 'lon': None, 'count': 0}}

        if remove_locations is None:
            remove_locations = []

        if start_date is None or end_date is None:
            pageviews = self.select_related('visitor')
        else:
            pageviews = self.filter(
                visitor__start_time__lt=end_date,
                visitor__start_time__gte=start_date,
            ).select_related('visitor')

        # filter out agents from the pageviews
        if filter_agents is not None:
            for agent in filter_agents:
                pageviews = pageviews.exclude(visitor__user_agent__contains=agent)
                # pageviews = pageviews.exclude(reduce(operator.and_, (Q(visitor__user_agent__contains=x) for x in filter_agents)))

        # get all the unique urls

        stats = {
            'total': 0,
            'unique': 0,
            'url_stats': [],
        }

        visitor_stats = {

        }

        dir_path = os.path.dirname(os.path.realpath(__file__))
        ip_reader = geoip2.database.Reader(os.path.join(dir_path, 'templates/tracking/GeoLite2-City_20190813/GeoLite2-City.mmdb'))

        ip_track = []

        # lets also track the daily views
        daily_views = {}


        # go through all the selected urls and count up
        if TRACK_SELECTED_URLS is not None:
            for url in TRACK_SELECTED_URLS:
                url = url.lstrip('^')
                count = pageviews.filter(url__contains=url).count()
                actual_count = 0
                unique_count = 0
                if count > 0:
                    # create the visitor list
                    visitors = []
                    for pageview in pageviews.filter(url__contains=url):
                    # for ip, agent in zip(list(pageviews.filter(url__contains=url).values('visitor__ip_address')),
                    #                      list(pageviews.filter(url__contains=url).values('visitor__user_agent'))):

                        ip = pageview.visitor.ip_address
                        agent = pageview.visitor.user_agent
                        time = pageview.view_time
                        # try to get the locaton
                        add_location = False
                        try:
                            location = '{0}, {1}'.format(ip_reader.city(ip).city.names['en'], ip_reader.city(ip).country.names['en'])
                            if location not in remove_locations:
                                add_location = True
                                if geo_location.get(location, None) is None:
                                    geo_location[location] = {'lon': ip_reader.city(ip).location.longitude,
                                                              'lat': ip_reader.city(ip).location.latitude,
                                                              'count': 1}
                                else:
                                    geo_location[location]['count'] += 1
                        except:
                            if 'None' not in remove_locations:
                                add_location = True
                                location = 'Could not find location'
                                geo_location['None']['count'] += 1

                        # make sure this location should be added
                        if add_location:
                            # add to this date
                            if daily_views.get(time.date(), None) is None:
                                daily_views[time.date()] = 1
                            else:
                                daily_views[time.date()] += 1
                            actual_count += 1
                            if ip not in ip_track:
                                ip_track.append(ip)
                                unique_count += 1
                            visitors.append({'ip': ip, 'location': location, 'agent': agent, 'time': time,
                                             'mouse click': 'not recorded' if pageview.visitor.mouse_click is None else pageview.visitor.mouse_click,
                                             'mouse move': 'not recorded' if pageview.visitor.mouse_movement is None else pageview.visitor.mouse_movement})

                            # print('{0}, {1}'.format(ip_reader.city(ip).city.names['en'], ip_reader.city(ip).country.names['en']))
                    # stats['url_stats'].append({'url': url, 'total_count': count,
                    #                            'unique_count': pageviews.filter(url__contains=url).values('visitor').distinct().count(),
                    #                            'visitors': visitors
                    #                            })
                    stats['url_stats'].append({'url': url, 'total_count': actual_count,
                                               'unique_count': unique_count,
                                               'visitors': visitors
                                               })
                    # visitor_stats[]
        # reader = geoip2.database.Reader('./GeoLite2-City_20190813/GeoLite2-City.mmdb')
        # a = '{0}, {1}'.format(reader.city('128.12.146.31').city.names['en'], reader.city('128.12.146.31').country.names['en'])

        stats['total'] = total_views = pageviews.count()
        unique_count = 0

        if not total_views:
            return stats

        # Registered user sessions
        registered_pageviews = pageviews.filter(visitor__user__isnull=False)
        registered_count = registered_pageviews.count()

        if registered_count:
            registered_unique_count = registered_pageviews.values(
                'visitor', 'url').distinct().count()

            # Update the total unique count...
            unique_count += registered_unique_count

            stats['registered'] = {
                'total': registered_count,
                'unique': registered_unique_count,
            }

        if TRACK_ANONYMOUS_USERS and not registered_only:
            guest_pageviews = pageviews.filter(visitor__user__isnull=True)
            guest_count = guest_pageviews.count()

            if guest_count:
                guest_unique_count = guest_pageviews.values(
                    'visitor', 'url').distinct().count()

                # Update the total unique count...
                unique_count += guest_unique_count

                stats['guests'] = {
                    'total': guest_count,
                    'unique': guest_unique_count,
                }

        # Finish setting the total visitor counts
        stats['unique'] = unique_count

        # save the geo location stats
        stats['geo_location'] = geo_location

        # save the daily views
        stats['daily views'] = daily_views

        return stats

    def exclude_from_query_set(self, query, values):
        return query.exclues(reduce(operator.and_, (Q(first_name__contains=x) for x in values)))

    def filter_from_query_set(self, query, values):
        return query.filter(reduce(operator.and_, (Q(first_name__contains=x) for x in values)))
