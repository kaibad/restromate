
from django.core.management.base import BaseCommand
from orders.models import Table

class Command(BaseCommand):
    help = 'Helps to pupulate/seed/config restraunt tables'

    def add_arguments(self, parser):
        parser.add_argument('--n',type=int,help='Number of tables',default=10)

    def handle(self, *args, **options):
        no_of_tables = options['n']
        created_count = 0

        for number in range(1,no_of_tables+1):
           table, created = Table.objects.get_or_create(name=f"Table {number}",defaults={'is_reserved':False})

           if created:
              created_count += 1



        self.stdout.write(self.style.SUCCESS(f'{created_count} new tables created successfully!'))