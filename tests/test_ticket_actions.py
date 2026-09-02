from datetime import timedelta
from typing import ClassVar

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from helpdesk import settings as helpdesk_settings
from helpdesk.models import CustomField, Queue, Ticket
from helpdesk.templatetags.ticket_to_link import num_to_link
from helpdesk.user import HelpdeskUser

try:  # python 3
    from urllib.parse import urlparse
except ImportError:  # python 2
    from urlparse import urlparse


class TicketActionsTestCase(TestCase):
    fixtures: ClassVar[list] = ["emailtemplate.json"]

    def setUp(self):
        self.queue_public = Queue.objects.create(
            title="Queue 1",
            slug="q1",
            allow_public_submission=True,
            new_ticket_cc="new.public@example.com",
            updated_ticket_cc="update.public@example.com",
        )

        self.queue_private = Queue.objects.create(
            title="Queue 2",
            slug="q2",
            allow_public_submission=False,
            new_ticket_cc="new.private@example.com",
            updated_ticket_cc="update.private@example.com",
        )

        self.ticket_data = {
            "queue": self.queue_public,
            "title": "Test Ticket",
            "description": "Some Test Ticket",
        }

        self.client = Client()
        helpdesk_settings.HELPDESK_ENABLE_PER_QUEUE_STAFF_PERMISSION = False

    def loginUser(self, is_staff=True):
        """Create a staff user and login"""
        User = get_user_model()
        self.user = User.objects.create(
            username="User_1",
            is_staff=is_staff,
        )
        self.user.set_password("pass")
        self.user.save()
        self.client.login(username="User_1", password="pass")

    def test_ticket_markdown(self):
        ticket_data = {
            "queue": self.queue_public,
            "title": "Test Ticket",
            "description": "*bold*",
        }

        ticket = Ticket.objects.create(**ticket_data)
        self.assertEqual(ticket.get_markdown(), "<p><em>bold</em></p>")

    def test_delete_ticket_staff(self):
        # make staff user
        self.loginUser()

        """Tests whether staff can delete tickets"""
        ticket = Ticket.objects.create(**self.ticket_data)
        ticket_id = ticket.id

        response = self.client.get(
            reverse("helpdesk:delete", kwargs={"ticket_id": ticket_id}), follow=True
        )
        self.assertContains(response, "Are you sure you want to delete this ticket")

        response = self.client.post(
            reverse("helpdesk:delete", kwargs={"ticket_id": ticket_id}), follow=True
        )
        first_redirect = response.redirect_chain[0]
        first_redirect_url = first_redirect[0]

        # Ensure we landed on the "View" page.
        # Django 1.9 compatible way of testing this
        # https://docs.djangoproject.com/en/1.9/releases/1.9/#http-redirects-no-longer-forced-to-absolute-uris
        urlparts = urlparse(first_redirect_url)
        self.assertEqual(urlparts.path, reverse("helpdesk:home"))

        # test ticket deleted
        with self.assertRaises(Ticket.DoesNotExist):
            Ticket.objects.get(pk=ticket_id)

    def test_update_ticket_staff(self):
        """Tests whether staff can update ticket details"""

        # make staff user
        self.loginUser()

        # create second user
        User = get_user_model()
        self.user2 = User.objects.create(
            username="User_2",
            is_staff=True,
        )

        initial_data = {
            "title": "Private ticket test",
            "queue": self.queue_public,
            "assigned_to": self.user,
            "status": Ticket.OPEN_STATUS,
        }

        # create ticket
        ticket = Ticket.objects.create(**initial_data)
        ticket_id = ticket.id

        default_post_data = {
            "title": ticket.title,
            "priority": ticket.priority,
            "queue": ticket.queue_id,
        }
        # assign new owner
        post_data = {
            "owner": self.user2.id,
            **default_post_data,
        }
        response = self.client.post(
            reverse("helpdesk:update", kwargs={"ticket_id": ticket_id}),
            post_data,
            follow=True,
        )
        self.assertContains(response, "Changed Owner from User_1 to User_2")

        # change status with users email assigned and submitter email assigned,
        # which triggers emails being sent
        ticket.assigned_to = self.user2
        ticket.submitter_email = "submitter@test.com"
        ticket.save()
        self.user2.email = "user2@test.com"
        self.user2.save()
        self.user.email = "user1@test.com"
        self.user.save()
        post_data = {
            "new_status": Ticket.CLOSED_STATUS,
            "public": True,
            **default_post_data,
        }

        # do this also to a newly assigned user (different from logged in one)
        ticket.assigned_to = self.user
        response = self.client.post(
            reverse("helpdesk:update", kwargs={"ticket_id": ticket_id}),
            post_data,
            follow=True,
        )
        self.assertContains(response, "Changed Status from Open to Closed")
        post_data = {
            "new_status": Ticket.OPEN_STATUS,
            "owner": self.user2.id,
            "public": True,
            **default_post_data,
        }
        response = self.client.post(
            reverse("helpdesk:update", kwargs={"ticket_id": ticket_id}),
            post_data,
            follow=True,
        )
        self.assertContains(response, "Changed Status from Open to Closed")

    def test_can_access_ticket(self):
        """Tests whether non-staff but assigned user still counts as owner"""

        # make non-staff user
        self.loginUser(is_staff=False)

        # create second user
        User = get_user_model()
        self.user2 = User.objects.create(
            username="User_2",
            is_staff=False,
        )

        initial_data = {
            "title": "Private ticket test",
            "queue": self.queue_private,
            "assigned_to": self.user,
            "status": Ticket.OPEN_STATUS,
        }

        # create ticket
        helpdesk_settings.HELPDESK_ENABLE_PER_QUEUE_STAFF_PERMISSION = True
        ticket = Ticket.objects.create(**initial_data)
        self.assertEqual(HelpdeskUser(self.user).can_access_ticket(ticket), True)
        self.assertEqual(HelpdeskUser(self.user2).can_access_ticket(ticket), False)

    def test_num_to_link(self):
        """Test that we are correctly expanding links to tickets from IDs"""

        # make staff user
        self.loginUser()

        initial_data = {
            "title": "Some private ticket",
            "queue": self.queue_public,
            "assigned_to": self.user,
            "status": Ticket.OPEN_STATUS,
        }

        # create ticket
        ticket = Ticket.objects.create(**initial_data)
        ticket_id = ticket.id

        # generate the URL text
        result = num_to_link(f"this is ticket#{ticket_id}")
        self.assertEqual(
            result,
            f"this is ticket <a href='/tickets/{ticket_id}/' class='ticket_link_status ticket_link_status_Open'>#{ticket_id}</a>",
        )

        result2 = num_to_link(f"whoa another ticket is here #{ticket_id} huh")
        self.assertEqual(
            result2,
            f"whoa another ticket is here  <a href='/tickets/{ticket_id}/' class='ticket_link_status ticket_link_status_Open'>#{ticket_id}</a> huh",
        )

    def test_create_ticket_getform(self):
        self.loginUser()
        response = self.client.get(reverse("helpdesk:submit"), follow=True)
        self.assertEqual(response.status_code, 200)

        # TODO this needs to be checked further

    def test_merge_tickets(self):
        self.loginUser()

        # Create two tickets
        ticket_1 = Ticket.objects.create(
            queue=self.queue_public,
            title="Ticket 1",
            description="Description from ticket 1",
            submitter_email="user1@mail.com",
            status=Ticket.RESOLVED_STATUS,
            resolution="Awesome resolution for ticket 1",
        )
        ticket_1_follow_up = ticket_1.followup_set.create(title="Ticket 1 creation")
        ticket_1_cc = ticket_1.ticketcc_set.create(user=self.user)
        ticket_1_created = ticket_1.created
        due_date = timezone.now()
        ticket_2 = Ticket.objects.create(
            queue=self.queue_public,
            title="Ticket 2",
            description="Description from ticket 2",
            submitter_email="user2@mail.com",
            due_date=due_date,
            assigned_to=self.user,
        )
        ticket_2_follow_up = ticket_1.followup_set.create(title="Ticket 2 creation")
        ticket_2_cc = ticket_2.ticketcc_set.create(email="random@mail.com")

        # Create custom fields and set values for tickets
        custom_field_1 = CustomField.objects.create(
            name="test",
            label="Test",
            data_type="varchar",
        )
        ticket_1_field_1 = "This is for the test field"
        ticket_1.ticketcustomfieldvalue_set.create(
            field=custom_field_1, value=ticket_1_field_1
        )
        ticket_2_field_1 = "Another test text"
        ticket_2.ticketcustomfieldvalue_set.create(
            field=custom_field_1, value=ticket_2_field_1
        )
        custom_field_2 = CustomField.objects.create(
            name="number",
            label="Number",
            data_type="integer",
        )
        ticket_2_field_2 = "444"
        ticket_2.ticketcustomfieldvalue_set.create(
            field=custom_field_2, value=ticket_2_field_2
        )

        # Check that it correctly redirects to the intermediate page
        response = self.client.post(
            reverse("helpdesk:mass_update"),
            data={"ticket_id": [str(ticket_1.id), str(ticket_2.id)], "action": "merge"},
            follow=True,
        )
        redirect_url = "{}?tickets={}&tickets={}".format(
            reverse("helpdesk:merge_tickets"),
            ticket_1.id,
            ticket_2.id,
        )
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, ticket_1.description)
        self.assertContains(response, ticket_1.resolution)
        self.assertContains(response, ticket_1.submitter_email)
        self.assertContains(response, ticket_1_field_1)
        self.assertContains(response, ticket_2.description)
        self.assertContains(response, ticket_2.submitter_email)
        self.assertContains(response, ticket_2_field_1)
        self.assertContains(response, ticket_2_field_2)

        # Check that the merge is correctly done
        response = self.client.post(
            redirect_url,
            data={
                "chosen_ticket": str(ticket_1.id),
                "due_date": str(ticket_2.id),
                "status": str(ticket_1.id),
                "submitter_email": str(ticket_2.id),
                "description": str(ticket_2.id),
                "assigned_to": str(ticket_2.id),
                custom_field_1.name: str(ticket_1.id),
                custom_field_2.name: str(ticket_2.id),
            },
            follow=True,
        )
        self.assertRedirects(response, ticket_1.get_absolute_url())
        ticket_2.refresh_from_db()
        self.assertEqual(ticket_2.merged_to, ticket_1)
        self.assertEqual(ticket_2.followup_set.count(), 0)
        self.assertEqual(ticket_2.ticketcc_set.count(), 0)
        ticket_1.refresh_from_db()
        self.assertEqual(ticket_1.created, ticket_1_created)
        self.assertEqual(ticket_1.due_date, due_date)
        self.assertEqual(ticket_1.status, Ticket.RESOLVED_STATUS)
        self.assertEqual(ticket_1.submitter_email, ticket_2.submitter_email)
        self.assertEqual(ticket_1.description, ticket_2.description)
        self.assertEqual(ticket_1.assigned_to, ticket_2.assigned_to)
        self.assertEqual(
            ticket_1.ticketcustomfieldvalue_set.get(field=custom_field_1).value,
            ticket_1_field_1,
        )
        self.assertEqual(
            ticket_1.ticketcustomfieldvalue_set.get(field=custom_field_2).value,
            ticket_2_field_2,
        )
        self.assertEqual(
            list(ticket_1.followup_set.all()), [ticket_1_follow_up, ticket_2_follow_up]
        )
        self.assertEqual(list(ticket_1.ticketcc_set.all()), [ticket_1_cc, ticket_2_cc])

    def test_update_ticket_queue(self):
        """Tests whether user can change the queue in the Respond to this ticket section."""

        # log user in
        self.loginUser()

        # create ticket
        initial_data = {
            "title": "Queue change ticket test",
            "queue": self.queue_public,
            "assigned_to": self.user,
            "status": Ticket.OPEN_STATUS,
        }
        ticket = Ticket.objects.create(**initial_data)
        ticket_id = ticket.id

        # initial queue
        self.assertEqual(ticket.queue, self.queue_public)

        # POST first follow-up with new queue
        new_queue = Queue.objects.create(
            title="New Queue",
            slug="newqueue",
        )
        comment_string = "first follow-up in new queue"
        post_data = {
            "title": ticket.title,
            "priority": ticket.priority,
            "comment": comment_string,
            "queue": str(new_queue.id),
        }
        self.client.post(
            reverse("helpdesk:update", kwargs={"ticket_id": ticket_id}), post_data
        )

        # queue was correctly modified
        ticket.refresh_from_db()
        self.assertEqual(ticket.queue, new_queue)

        # ticket change was saved
        latest_fup = ticket.followup_set.latest("date")
        latest_ticketchange = latest_fup.ticketchange_set.latest("id")
        self.assertEqual(latest_ticketchange.field, _("Queue"))
        self.assertEqual(int(latest_ticketchange.old_value), self.queue_public.id)
        self.assertEqual(int(latest_ticketchange.new_value), new_queue.id)
        self.assertEqual(latest_fup.comment, comment_string)

    def test_update_ticket_with_custom_fields(self):
        """Tests that tickets that contain custom fields will correctly update core and custom fields."""

        # log user in
        self.loginUser()

        # create ticket
        initial_data = {
            "title": "Queue change ticket test",
            "queue": self.queue_public,
            "assigned_to": self.user,
            "status": Ticket.OPEN_STATUS,
        }
        ticket = Ticket.objects.create(**initial_data)
        ticket_id = ticket.id
        # Create custom fields and set values for tickets
        custom_field_1 = CustomField.objects.create(
            name="my_custom_field",
            label="My Custom Field",
            data_type="varchar",
            required=True,
        )
        custom_field_1_value = "This is my custom field value"

        comment_string = "FollowUp.comment field string"
        post_data = {
            "title": ticket.title,
            "priority": ticket.priority,
            "comment": comment_string,
            "queue": str(self.queue_public.id),
            "custom_" + custom_field_1.name: custom_field_1_value,
        }
        self.client.post(
            reverse("helpdesk:update", kwargs={"ticket_id": ticket_id}), post_data
        )

        # queue was correctly modified
        ticket.refresh_from_db()
        self.assertEqual(ticket.queue_id, self.queue_public.id)

        # ticket change was saved
        latest_fup = ticket.followup_set.latest("date")
        self.assertEqual(latest_fup.comment, comment_string)
        self.assertEqual(
            ticket.ticketcustomfieldvalue_set.get(field=custom_field_1).value,
            custom_field_1_value,
        )

    def test_edit_ticket_priority_creates_history(self):
        """T1: Changing ticket priority via Actions -> Edit Ticket records history and acting user."""
        self.loginUser()

        ticket = Ticket.objects.create(
            queue=self.queue_public,
            title="Priority Edit Test Ticket",
            description="Testing priority change",
            priority=3,
        )
        self.assertEqual(ticket.followup_set.count(), 0)

        post_data = {
            "title": ticket.title,
            "queue": ticket.queue.id,
            "priority": 1,
            "description": ticket.description,
        }
        response = self.client.post(
            reverse("helpdesk:edit", kwargs={"ticket_id": ticket.id}),
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("helpdesk:view", kwargs={"ticket_id": ticket.id}))

        ticket.refresh_from_db()
        self.assertEqual(ticket.priority, 1)

        self.assertEqual(ticket.followup_set.count(), 1)
        followup = ticket.followup_set.latest("date")
        self.assertEqual(followup.user, self.user)

        priority_change = followup.ticketchange_set.filter(field=_("Priority")).first()
        self.assertIsNotNone(priority_change)
        self.assertEqual(str(priority_change.old_value), "3")
        self.assertEqual(str(priority_change.new_value), "1")

    def test_edit_ticket_queue_creates_history(self):
        """T2: Changing ticket queue via Actions -> Edit Ticket records history and acting user."""
        self.loginUser()

        ticket = Ticket.objects.create(
            queue=self.queue_public,
            title="Queue Edit Test Ticket",
            description="Testing queue change",
            priority=3,
        )
        self.assertEqual(ticket.followup_set.count(), 0)

        post_data = {
            "title": ticket.title,
            "queue": self.queue_private.id,
            "priority": ticket.priority,
            "description": ticket.description,
        }
        response = self.client.post(
            reverse("helpdesk:edit", kwargs={"ticket_id": ticket.id}),
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("helpdesk:view", kwargs={"ticket_id": ticket.id}))

        ticket.refresh_from_db()
        self.assertEqual(ticket.queue, self.queue_private)

        self.assertEqual(ticket.followup_set.count(), 1)
        followup = ticket.followup_set.latest("date")
        self.assertEqual(followup.user, self.user)

        queue_change = followup.ticketchange_set.filter(field=_("Queue")).first()
        self.assertIsNotNone(queue_change)
        self.assertEqual(str(queue_change.old_value), str(self.queue_public.id))
        self.assertEqual(str(queue_change.new_value), str(self.queue_private.id))

    def test_edit_ticket_due_date_creates_history(self):
        """T3: Changing ticket due date via Actions -> Edit Ticket records history and acting user."""
        self.loginUser()

        ticket = Ticket.objects.create(
            queue=self.queue_public,
            title="Due Date Edit Test Ticket",
            description="Testing due date change",
            priority=3,
        )
        self.assertIsNone(ticket.due_date)
        self.assertEqual(ticket.followup_set.count(), 0)

        new_due_date = (timezone.now() + timedelta(days=7)).replace(microsecond=0)
        post_data = {
            "title": ticket.title,
            "queue": ticket.queue.id,
            "priority": ticket.priority,
            "due_date": new_due_date.strftime("%Y-%m-%d %H:%M:%S"),
            "description": ticket.description,
        }
        response = self.client.post(
            reverse("helpdesk:edit", kwargs={"ticket_id": ticket.id}),
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("helpdesk:view", kwargs={"ticket_id": ticket.id}))

        ticket.refresh_from_db()
        self.assertIsNotNone(ticket.due_date)

        self.assertEqual(ticket.followup_set.count(), 1)
        followup = ticket.followup_set.latest("date")
        self.assertEqual(followup.user, self.user)

        due_date_change = followup.ticketchange_set.filter(field=_("Due on")).first()
        self.assertIsNotNone(due_date_change)

    def test_edit_ticket_multiple_fields_creates_history(self):
        """T4: Changing multiple fields via Actions -> Edit Ticket records comprehensive history."""
        self.loginUser()

        custom_field = CustomField.objects.create(
            name="notes",
            label="Notes",
            data_type="varchar",
            required=False,
        )

        ticket = Ticket.objects.create(
            queue=self.queue_public,
            title="Original Title",
            description="Initial Description",
            priority=3,
        )
        ticket.ticketcustomfieldvalue_set.create(
            field=custom_field,
            value="Old note",
        )
        self.assertEqual(ticket.followup_set.count(), 0)

        new_due_date = (timezone.now() + timedelta(days=5)).replace(microsecond=0)
        post_data = {
            "title": "Updated Title",
            "queue": self.queue_private.id,
            "priority": 2,
            "due_date": new_due_date.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Updated Description",
            "custom_notes": "New note",
        }
        response = self.client.post(
            reverse("helpdesk:edit", kwargs={"ticket_id": ticket.id}),
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("helpdesk:view", kwargs={"ticket_id": ticket.id}))

        ticket.refresh_from_db()
        self.assertEqual(ticket.title, "Updated Title")
        self.assertEqual(ticket.queue, self.queue_private)
        self.assertEqual(ticket.priority, 2)
        self.assertEqual(ticket.description, "Updated Description")
        self.assertEqual(
            ticket.ticketcustomfieldvalue_set.get(field=custom_field).value,
            "New note",
        )

        # Single FollowUp should be created for this entire batch edit
        self.assertEqual(ticket.followup_set.count(), 1)
        followup = ticket.followup_set.latest("date")
        self.assertEqual(followup.user, self.user)

        # Verify all individual ticket change records
        changes = {c.field: (c.old_value, c.new_value) for c in followup.ticketchange_set.all()}
        self.assertIn(str(_("Title")), changes)
        self.assertEqual(changes[str(_("Title"))], ("Original Title", "Updated Title"))

        self.assertIn(str(_("Priority")), changes)
        self.assertEqual(changes[str(_("Priority"))], ("3", "2"))

        self.assertIn(str(_("Queue")), changes)
        self.assertEqual(
            changes[str(_("Queue"))],
            (str(self.queue_public.id), str(self.queue_private.id)),
        )

        self.assertIn(str(_("Description")), changes)
        self.assertEqual(
            changes[str(_("Description"))],
            ("Initial Description", "Updated Description"),
        )

        self.assertIn("notes", changes)
        self.assertEqual(changes["notes"], ("Old note", "New note"))

        self.assertIn(str(_("Due on")), changes)

