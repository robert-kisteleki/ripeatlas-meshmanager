from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from meshmgr.models import CountryMesh


class Command(BaseCommand):
    args = '(none)'
    help = 'Add a new country to measure.'

    option_list = BaseCommand.option_list + (
        make_option(
            '--cc',
            action='store',
            dest='cc',
            default=None,
            help='ISO 3166-1 2 letter country code'
        ),
        make_option(
            '--continent',
            action='store',
            dest='continent',
            default=None,
            help='2 letter continent code (EU,NA,SA,AF,AS,AP)'
        ),
        make_option(
            '--name',
            action='store',
            dest='name',
            default=None,
            help='Country name'
        ),
    )

    def handle(self, *args, **options):

        if not options['cc'] or not options['name'] or not options['continent']:
            raise CommandError('You must specify all parameters')

        country = CountryMesh.objects.filter(iso3166=options['cc'])
        if country:
            print('%s is already measured' % country[0])
        else:
            print('Adding %s' % options['cc'])
            country = CountryMesh()
            country.continent = options['continent']
            country.iso3166 = options['cc']
            country.country_name = options['name']
            country.save()