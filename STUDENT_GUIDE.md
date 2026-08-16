# django-helpdesk — Student Comprehension Project

This repository contains a classroom-ready version of
[django-helpdesk](https://github.com/django-helpdesk/django-helpdesk), a substantial
open-source Django application for managing support tickets.

The purpose of this repository is **not to teach you django-helpdesk file by file**.
Instead, you will use a working system, observe its behaviour, form hypotheses about
how it works, and gradually trace those behaviours through the code.

The repository includes a small demo organisation called **Northstar Services** so
that you can start using the system quickly.

---

## 1. What does django-helpdesk do?

django-helpdesk is a ticket-based support system.

A customer can report a problem by creating a ticket. Support agents then receive,
assign, investigate, update and resolve those tickets.

A typical flow looks like:

```text
Customer reports a problem
          ↓
      Ticket created
          ↓
Support agent sees the ticket
          ↓
Ticket is assigned / worked on
          ↓
Agent updates its status
          ↓
      Ticket resolved
          ↓
Customer sees the resolution
```

The actual application is much richer than this simple flow. Part of your work will
be discovering how that larger system is organised.

---

# 2. Setup

## Clone the repository

```bash
git clone <repository-url>
cd django-helpdesk-comprehension
```

## Create a Python virtual environment

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

You should now see something similar to:

```text
(.venv)
```

at the beginning of your terminal prompt.

## Install the project

From the **repository root**, run:

```bash
python3 -m pip install -e .
```

On a system where Python is available as `python` rather than `python3`, use:

```bash
python -m pip install -e .
```

The final `.` is important. It tells `pip` to install the project in the current
directory.

---

# 3. Prepare the student demo

The student-facing Django project lives in:

```text
student_demo/
```

First create its database:

```bash
python3 student_demo/manage.py migrate
```

Then load the demo organisation, users, queues and sample tickets:

```bash
python3 student_demo/manage.py load_demo
```

You should see a message confirming that the demo data was loaded.

---

# 4. Run the application

Start the student demo with:

```bash
python3 student_demo/manage.py runserver
```

Django will normally start at:

```text
http://127.0.0.1:8000/
```

Open that address in your browser.

**Important:** use:

```bash
python3 student_demo/manage.py runserver
```

and not the repository's other `manage.py`. This repository also contains the
original django-helpdesk demo project.

### If port 8000 is already in use

You may see an error saying that the port is already in use.

Either stop the other server or use another port:

```bash
python3 student_demo/manage.py runserver 8001
```

Then open:

```text
http://127.0.0.1:8001/
```

---

# 5. Meet Northstar Services

The demo represents the internal support desk of **Northstar Services**.

It has three support queues:

- IT Support
- Workplace & Facilities
- People Operations

There are three kinds of users.

| Role | User | Username | Password |
|---|---|---|---|
| Customer | Maya Sen | `maya` | `demo123` |
| Customer | Rahul Mehta | `rahul` | `demo123` |
| Support Agent | Anita Rao | `anita` | `demo123` |
| Support Agent | Vikram Shah | `vikram` | `demo123` |
| Manager | Manager | `manager` | `demo123` |

These accounts exist only for the local classroom demo.

---

# 6. Start by role-playing the system

Do not start by reading the source code.

First understand the product from the perspective of its users.

Work in a small group and divide the roles.

## Customer

Log in as **Maya**.

Explore **My Tickets**.

Then create a new ticket describing a realistic problem, for example:

> My laptop cannot connect to the office Wi-Fi.

Notice what information the system asks for and what happens after the ticket is
created.

Customers in this demo can create tickets and return later to watch their status
and read public updates from the support team.

## Support Agent

Log out and return to the Northstar landing page.

Now log in as **Anita**.

Find Maya's new ticket.

Explore what an agent can do with it. For example:

- assign or take responsibility for it;
- add an update;
- change its status;
- investigate the information recorded with the ticket;
- resolve it.

Pay attention to how the agent's interface differs from the customer's interface.

## Customer again

Log out and log back in as **Maya**.

Open **My Tickets**.

Find the ticket you created earlier.

What changed?

Can Maya see the agent's response? Can she understand the current state of the
ticket?

## Manager

Finally, enter through the **Manager** role.

Explore the administrative view of the system.

Notice that a manager sees the system differently from both customers and support
agents.

---

# 7. Now start comprehending the system

Once you understand the basic product flow, start connecting behaviour to code.

Do **not** try to read the repository from beginning to end.

Instead, choose a behaviour and trace it.

For example:

> What happens when Maya creates a ticket?

Turn that into smaller questions:

```text
Which URL receives the request?
        ↓
Which Django view handles it?
        ↓
Which form processes the input?
        ↓
Which model represents a ticket?
        ↓
Where is the ticket saved?
        ↓
How is its initial status determined?
        ↓
Where does the user get redirected?
```

You can do the same for other behaviours:

- How does **My Tickets** know which tickets belong to Maya?
- How does an agent change a ticket's status?
- How does assignment work?
- What determines which queues an agent can see?
- What happens when a ticket is resolved?
- What permissions distinguish customers from agents?
- How are URLs connected to views?
- How are templates selected?

A useful comprehension cycle is:

```text
Observe behaviour
      ↓
Ask a precise question
      ↓
Form a hypothesis
      ↓
Find relevant code
      ↓
Trace the execution path
      ↓
Test your explanation
```

The objective is not merely to find code. It is to develop an explanation of **why
the system behaves as it does**.

---

# 8. Repository structure

Two parts of the repository are especially important.

```text
django-helpdesk-comprehension/
│
├── student_demo/
│   ├── config/
│   ├── demo/
│   ├── demo_data/
│   ├── templates/
│   └── manage.py
│
└── src/
    └── helpdesk/
```

## `student_demo/`

This is the small Django project created for the classroom.

It provides:

- the Northstar landing page;
- role-oriented login flows;
- demo users;
- demo queues and tickets;
- demo configuration;
- a few template customisations.

It is deliberately small.

Reading this code can help you understand **how another Django project uses
django-helpdesk as an application**.

## `src/helpdesk/`

This is the actual django-helpdesk application.

Most of the substantial system behaviour lives here.

As your investigation becomes deeper, you will spend more time tracing code inside
this directory.

A useful mental model is:

```text
student_demo
    │
    │ configures and presents
    ▼
django-helpdesk
    │
    │ implements
    ▼
ticket-management behaviour
```

---

# 9. Django template overrides

You may notice files such as:

```text
student_demo/templates/helpdesk/
```

even though django-helpdesk itself already contains templates under:

```text
src/helpdesk/templates/helpdesk/
```

This is intentional.

Django allows the project using an application to override selected templates from
that application.

The student demo uses this mechanism to simplify parts of the user experience
without rewriting the underlying django-helpdesk application.

This distinction is useful when studying reusable Django applications:

```text
Reusable application
        +
Host-project configuration/customisation
        =
Final application experienced by the user
```

---

# 10. Demo configuration

The Northstar demo data is defined in:

```text
student_demo/demo_data/company.json
```

It contains information such as the organisation, demo users, queues and sample
tickets.

The command:

```bash
python3 student_demo/manage.py load_demo
```

reads this configuration and prepares the demo.

After you understand the original setup, your instructor may ask you to modify or
extend this configuration.

---

# 11. Important choices in this classroom demo

The student demo intentionally simplifies some aspects of django-helpdesk.

### Customers are authenticated

Customers log in so that they can easily return to **My Tickets** without relying
on email notifications.

### Customers create and monitor tickets

After creating a ticket, customers primarily watch its status and read public
updates from support agents.

Ticket management is performed by support agents.

### Email is not required

A production helpdesk would normally send email notifications. The classroom demo
does not require an SMTP server.

### Not every django-helpdesk feature is part of the first exercise

django-helpdesk contains capabilities beyond the initial role-play.

They have not necessarily been removed.

You will encounter more of the system as you investigate it.

---

# 12. Resetting the demo

If your instructor asks you to start again with a completely clean demo, stop the
server and remove the local database:

```bash
rm student_demo/db.sqlite3
```

Then recreate it:

```bash
python3 student_demo/manage.py migrate
python3 student_demo/manage.py load_demo
```

On Windows, delete `student_demo\db.sqlite3` using File Explorer or the appropriate
command-line command.

Then restart:

```bash
python3 student_demo/manage.py runserver
```

Do not delete the database merely because you are restarting the server.

---

# 13. Troubleshooting

### `-e option requires 1 argument`

You probably ran:

```bash
python3 -m pip install -e
```

The command must end with a dot:

```bash
python3 -m pip install -e .
```

### `python3` is not found

Try:

```bash
python --version
```

If that works, substitute `python` for `python3` in the commands above.

### Port already in use

Use another port:

```bash
python3 student_demo/manage.py runserver 8001
```

### I see the wrong demo/application

Make sure you started:

```bash
python3 student_demo/manage.py runserver
```

rather than another `manage.py` in the repository.

### I changed Python code but behaviour looks unchanged

Stop the development server with `Ctrl+C` and start it again.

---

# 14. About the original project

This repository is based on the open-source **django-helpdesk** project.

The original project contains considerably more functionality, documentation and
history than the classroom demo exposes initially.

As you become comfortable with the system, the original project's documentation,
issues, tests and commit history can themselves become useful sources of evidence
when trying to understand why the system behaves in a particular way.

The classroom modifications in `student_demo/` are intended to make it easier to
enter the system and study it; they are not a replacement for the underlying
django-helpdesk application.

---

## Your first objective

Before trying to change anything, make sure you can explain this flow:

```text
Customer creates ticket
        ↓
Agent discovers ticket
        ↓
Agent works on ticket
        ↓
Ticket changes state
        ↓
Customer observes the change
```

Then pick **one transition in that flow** and find the code responsible for making
it happen.

That is where system comprehension begins.