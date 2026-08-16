from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.utils import timezone

from helpdesk.models import FollowUp, Queue, Ticket

from demo.company import load_company_config


STATUS_MAP = {
    "open": Ticket.OPEN_STATUS,
    "reopened": Ticket.REOPENED_STATUS,
    "resolved": Ticket.RESOLVED_STATUS,
    "closed": Ticket.CLOSED_STATUS,
    "duplicate": Ticket.DUPLICATE_STATUS,
}


class Command(BaseCommand):
    help = "Create or update the classroom helpdesk demo company."

    def handle(self, *args, **options):
        data = load_company_config()
        organization = data["organization"]

        self.stdout.write(
            self.style.SUCCESS(f"Loading demo company: {organization['name']}")
        )

        users = self._load_users(data["users"])
        queues = self._load_queues(data["queues"], users)
        self._load_tickets(data.get("tickets", []), users, queues)

        Site.objects.update_or_create(
            pk=1,
            defaults={
                "domain": "127.0.0.1:8000",
                "name": organization["name"],
            },
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo is ready."))
        self.stdout.write("Open http://127.0.0.1:8000/")
        self.stdout.write("")
        self.stdout.write("Classroom accounts:")
        for role_group in ("customers", "agents"):
            for item in data["users"][role_group]:
                self.stdout.write(
                    f"  {item['role_label']}: {item['username']} / {item['password']}"
                )
        manager = data["users"]["manager"]
        self.stdout.write(
            f"  {manager['role_label']}: "
            f"{manager['username']} / {manager['password']}"
        )

    def _load_users(self, users_data):
        User = get_user_model()
        users = {}

        for role_group in ("customers", "agents"):
            for item in users_data[role_group]:
                is_staff = role_group == "agents"
                user, _ = User.objects.update_or_create(
                    username=item["username"],
                    defaults={
                        "first_name": item["first_name"],
                        "last_name": item["last_name"],
                        "email": item["email"],
                        "is_staff": is_staff,
                        "is_superuser": False,
                        "is_active": True,
                    },
                )
                user.set_password(item["password"])
                user.save()
                users[item["username"]] = user

        item = users_data["manager"]
        manager, _ = User.objects.update_or_create(
            username=item["username"],
            defaults={
                "first_name": item["first_name"],
                "last_name": item["last_name"],
                "email": item["email"],
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        manager.set_password(item["password"])
        manager.save()
        users[item["username"]] = manager

        return users

    def _load_queues(self, queues_data, users):
        queues = {}

        for item in queues_data:
            defaults = {
                "title": item["name"],
                "email_address": item["email"],
                "locale": "en",
                "allow_public_submission": True,
                "allow_email_submission": False,
                "escalate_days": None,
            }

            default_owner = item.get("default_owner")
            if default_owner:
                defaults["default_owner"] = users[default_owner]

            queue, _ = Queue.objects.update_or_create(
                slug=item["slug"],
                defaults=defaults,
            )
            queues[item["slug"]] = queue
            self.stdout.write(f"  Queue: {queue.title}")

        return queues

    def _load_tickets(self, tickets_data, users, queues):
        for item in tickets_data:
            submitter = users[item["submitter"]]
            assigned_to = (
                users[item["assigned_to"]] if item.get("assigned_to") else None
            )
            status = STATUS_MAP[item["status"].lower()]

            ticket, created = Ticket.objects.update_or_create(
                title=item["title"],
                submitter_email=submitter.email,
                defaults={
                    "queue": queues[item["queue"]],
                    "assigned_to": assigned_to,
                    "status": status,
                    "description": item["description"],
                    "priority": item.get("priority", 3),
                },
            )

            if created:
                ticket.created = timezone.now()
                ticket.save(update_fields=["created"])

            FollowUp.objects.update_or_create(
                ticket=ticket,
                title="Ticket Opened",
                defaults={
                    "date": ticket.created,
                    "comment": item["description"],
                    "public": True,
                    "user": submitter,
                },
            )

            if status in {
                Ticket.RESOLVED_STATUS,
                Ticket.CLOSED_STATUS,
            }:
                FollowUp.objects.update_or_create(
                    ticket=ticket,
                    title="Issue resolved",
                    defaults={
                        "date": timezone.now(),
                        "comment": item.get(
                            "resolution",
                            "The support team completed the requested work.",
                        ),
                        "public": True,
                        "user": assigned_to,
                        "new_status": status,
                    },
                )

            self.stdout.write(
                f"  Ticket: {ticket.ticket_for_url} - {ticket.title}"
            )
