# django-helpdesk — Student Comprehension Guide

This repository contains a classroom-ready version of
[django-helpdesk](https://github.com/django-helpdesk/django-helpdesk), a substantial
open-source Django application for managing support tickets.

The purpose of this exercise is **not to learn django-helpdesk file by file**.

Instead, you will:

1. use a working system;
2. observe its behaviour;
3. form hypotheses about how it works;
4. trace those behaviours through the code; and
5. eventually explain, debug and modify parts of the system.

The repository includes a small demo organisation called **Northstar Services** so
that you can start exploring the system quickly.

---

## 1. What does django-helpdesk do?

django-helpdesk is a ticket-based support system.

A customer reports a problem by creating a ticket. Support agents receive,
investigate, update and eventually resolve those tickets.

A simplified flow looks like this:

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

The actual application is much richer than this simple flow. Part of your work
will be discovering how that larger system is organised.

---

# 2. Prerequisites

Before starting, make sure you have the following installed:

- Git
- Python
- Node.js
- Yarn
- Make

Check them from the terminal:

```bash
git --version
python --version
node --version
yarn --version
make --version
```

Depending on your system, Python may initially be available as `python3` instead
of `python`. That is fine.

Once the virtual environment described below is activated, use `python` for the
remaining commands.

---

# 3. Clone the repository

Clone the repository and enter its directory:

```bash
git clone <repository-url>
cd django-helpdesk-comprehension
```

---

# 4. Create a Python virtual environment

If your system uses `python3`:

```bash
python3 -m venv .venv
```

If it uses `python`:

```bash
python -m venv .venv
```

On macOS/Linux, activate it with:

```bash
source .venv/bin/activate
```

On Windows:

```text
.venv\Scripts\activate
```

After activation, your terminal prompt should normally begin with something
similar to:

```text
(.venv)
```

Check that Python is now coming from the virtual environment:

```bash
python --version
```

---

# 5. Install django-helpdesk

From the repository root, with the virtual environment activated, run:

```bash
python -m pip install -e .
```

The final `.` is important.

It tells `pip` to install the Python project located in the current directory.

The `-e` means **editable installation**. Changes you make to the source code in
this repository will therefore be reflected when you run the application.

---

# 6. Set up the student demo

Run:

```bash
make student-setup
```

This performs the remaining first-time setup.

Behind the scenes it:

```text
yarn install
      ↓
installs frontend dependencies

make static-vendor
      ↓
copies required frontend libraries
into django-helpdesk's static directories

python student_demo/manage.py migrate
      ↓
creates/updates the database schema

python student_demo/manage.py load_demo
      ↓
creates the Northstar demo organisation,
users, queues and sample tickets
```

You normally need to run `student-setup` only when setting up a fresh copy of the
repository.

---

# 7. Run the application

Start the application with:

```bash
make student-run
```

Django will normally start the development server at:

```text
http://127.0.0.1:8000/
```

Open that address in your browser.

To stop the server, return to the terminal and press:

```text
Ctrl+C
```

The next time you want to work with the application, activate your virtual
environment and simply run:

```bash
make student-run
```

You do **not** need to run `student-setup` every time.

### If port 8000 is already in use

Another application may already be using port 8000.

You can either stop that application or run the Django server directly on another
port:

```bash
python student_demo/manage.py runserver 8001
```

Then open:

```text
http://127.0.0.1:8001/
```

---

# 8. Meet Northstar Services

The classroom demo represents the support desk of **Northstar Services**.

It has three support queues:

- IT Support
- Workplace & Facilities
- People Operations

The demo contains three kinds of users.

| Role | User | Username | Password |
|---|---|---|---|
| Customer | Maya Sen | `maya` | `demo123` |
| Customer | Rahul Mehta | `rahul` | `demo123` |
| Support Agent | Anita Rao | `anita` | `demo123` |
| Support Agent | Vikram Shah | `vikram` | `demo123` |
| Manager | Manager | `manager` | `demo123` |

These accounts exist only for the local classroom demo.

---

# 9. First understand the product

**Do not start by reading the source code.**

First understand the system from the perspective of the people who use it.

Work in a small group and divide the roles between yourselves.

Rotate roles later so that everyone experiences the system from different
perspectives.

---

## Customer

Enter through **Customer** and log in as Maya.

Explore **My Tickets**.

Then create a new ticket describing a realistic problem, for example:

> My laptop cannot connect to the office Wi-Fi.

Notice:

- what information the system asks for;
- which support queue receives the ticket;
- what identifier the ticket receives;
- what its initial status is; and
- what Maya can and cannot do after submitting it.

Customers in this demo can create tickets and return later to watch their status
and read public updates from the support team.

---

## Support Agent

Log out.

You should return to the Northstar landing page.

Now enter through **Support Agent** and log in as Anita.

Find Maya's new ticket.

Explore what an agent can do with it.

For example:

- take or assign responsibility for it;
- add an update;
- change its status;
- examine the information recorded with the ticket;
- work on it; and
- resolve it.

Pay attention to how the agent's interface differs from the customer's interface.

---

## Customer again

Log out and log back in as Maya.

Open **My Tickets** and find the ticket you created.

What changed?

Can Maya see the support agent's response?

Can she understand the current state of the ticket?

What information can the agent see that Maya cannot?

---

## Manager

Finally, log out and enter through **Manager**.

Explore the administrative interface.

Notice that a manager sees the system differently from both customers and support
agents.

Do not try to understand every option yet.

The purpose of this first exploration is simply to develop a mental model of the
system.

---

# 10. The basic mental model

After the role-play, you should be able to explain this flow:

```text
Customer
   │
   │ creates
   ▼
 Ticket
   │
   │ enters
   ▼
 Queue
   │
   │ handled by
   ▼
 Agent
   │
   │ changes
   ▼
Ticket state
   │
   │ observed by
   ▼
Customer
```

You should also begin noticing that the system contains concepts such as:

```text
User
Ticket
Queue
Status
Priority
Assignment
Comment / Follow-up
Resolution
```

At this stage, understanding what these concepts mean in the product is more
important than knowing where their code lives.

---

# 11. Now start comprehending the code

Once you understand the basic product flow, begin connecting observed behaviour
to source code.

Do **not** try to read the repository from beginning to end.

Instead, choose one behaviour and trace it.

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
Which model represents the ticket?
        ↓
Where is the ticket saved?
        ↓
How is its initial state determined?
        ↓
Where does the user get redirected?
```

You can investigate other behaviours in the same way:

- How does **My Tickets** know which tickets belong to Maya?
- How does an agent change a ticket's status?
- How does ticket assignment work?
- What determines which queues an agent can see?
- What happens when a ticket is resolved?
- What distinguishes customers from support agents?
- How are URLs connected to views?
- How does Django decide which template to render?

---

# 12. A useful comprehension process

For each investigation, follow a cycle like this:

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
      ↓
Revise your hypothesis if necessary
```

For example, suppose you observe:

> Anita can see a ticket that Maya created.

Do not immediately search randomly through the repository.

Instead ask:

> How does the dashboard decide which tickets Anita is allowed to see?

You might then form a hypothesis:

> Perhaps tickets are selected based on the queues assigned to Anita.

Now find evidence in the code that either supports or contradicts that
explanation.

The objective is not merely to locate code.

The objective is to build and test an **explanation of system behaviour**.

---

# 13. Repository structure

Two parts of the repository are particularly important for this exercise:

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

---

## `student_demo/`

This is the small Django project created specifically for the classroom exercise.

It provides:

- the Northstar landing page;
- role-oriented entry points;
- demo users;
- demo queues and tickets;
- demo configuration; and
- a few user-interface customisations.

It is deliberately small.

Reading this code can help you understand **how a Django project uses
django-helpdesk as a reusable application**.

---

## `src/helpdesk/`

This is the actual django-helpdesk application.

Most of the substantial ticket-management behaviour lives here.

As your investigations become deeper, you will spend more time tracing code inside
this directory.

A useful distinction is:

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

Do not confuse code that belongs to our classroom host application with code that
belongs to django-helpdesk itself.

---

# 14. Django template overrides

You may notice files under:

```text
student_demo/templates/helpdesk/
```

even though django-helpdesk itself already has templates under:

```text
src/helpdesk/templates/helpdesk/
```

This is intentional.

Django applications can provide their own templates, while the project using the
application can selectively override them.

The student demo uses this mechanism to simplify parts of the user experience
without rewriting the underlying django-helpdesk application.

This gives us an important architectural relationship:

```text
Reusable application
        +
Host-project configuration/customisation
        =
Application experienced by the user
```

When investigating behaviour, therefore, do not assume that everything visible in
the browser comes directly from `src/helpdesk/`.

---

# 15. Demo configuration

The Northstar demo data is defined in:

```text
student_demo/demo_data/company.json
```

It describes information used to prepare the classroom environment, including
demo users, support queues and sample tickets.

The management command:

```bash
python student_demo/manage.py load_demo
```

reads this configuration and prepares the demo.

The Makefile target:

```bash
make student-setup
```

runs this command for you during initial setup.

After you understand the original system, you may be asked to modify or extend
this configuration.

---

# 16. Important choices in this classroom demo

The classroom project deliberately simplifies some aspects of django-helpdesk.

## Customers are authenticated

Customers log in so that they can easily return to **My Tickets**.

A production helpdesk may use email links and other mechanisms to let customers
return to their tickets.

---

## Customers create and monitor tickets

In this demo, customers:

```text
create ticket
     ↓
return to My Tickets
     ↓
watch ticket status
     ↓
read public support updates
```

General ticket management is performed by support agents.

---

## Email is not required

A production helpdesk would normally use email notifications as an important part
of its workflow.

The classroom demo does not require an SMTP server.

Customers instead return to **My Tickets** to see what has happened.

---

## Not every django-helpdesk feature is part of the first exercise

django-helpdesk contains considerably more functionality than the initial
role-play exposes.

Those features have not necessarily been removed.

You will encounter more of the system as you investigate it.

---

# 17. Resetting the demo

Your database is stored locally in:

```text
student_demo/db.sqlite3
```

It is not part of the repository.

Normally you should **not** delete it. Your tickets and other changes remain there
between runs of the development server.

If your instructor asks you to return to a completely clean demo, stop the server
and delete:

```text
student_demo/db.sqlite3
```

On macOS/Linux:

```bash
rm student_demo/db.sqlite3
```

Then recreate the demo:

```bash
make student-setup
```

and start it again:

```bash
make student-run
```

---

# 18. Troubleshooting

## `-e option requires 1 argument`

You probably ran:

```bash
python -m pip install -e
```

The command must end with a dot:

```bash
python -m pip install -e .
```

---

## `python` is not found

Before creating the virtual environment, your machine may use:

```bash
python3
```

instead.

Create the environment with:

```bash
python3 -m venv .venv
```

After activating the virtual environment, `python` should normally be available.

---

## `yarn` is not found

The frontend dependencies have not been installed because Yarn is missing.

Check:

```bash
node --version
yarn --version
```

Install Node.js and Yarn before running:

```bash
make student-setup
```

---

## The page loads but looks broken or unstyled

If the server reports errors for files such as:

```text
/static/helpdesk/vendor/bootstrap/...
/static/helpdesk/vendor/jquery/...
/static/helpdesk/vendor/datatables/...
```

the frontend vendor assets have not been prepared.

Run:

```bash
make student-setup
```

and restart the server.

---

## Port 8000 is already in use

Either stop the process already using port 8000 or start Django on another port:

```bash
python student_demo/manage.py runserver 8001
```

Then visit:

```text
http://127.0.0.1:8001/
```

---

## I see the wrong demo/application

This repository also contains django-helpdesk's original demo project.

For the classroom exercise, use:

```bash
make student-run
```

which runs:

```text
student_demo/manage.py
```

---

## I changed Python code but behaviour looks unchanged

Django's development server normally reloads Python changes automatically, but if
necessary stop it with:

```text
Ctrl+C
```

and restart:

```bash
make student-run
```

---

# 19. About the original project

This repository is based on the open-source **django-helpdesk** project.

The original project contains substantially more functionality, documentation,
tests and development infrastructure than the classroom demo initially exposes.

The original project documentation remains available in this repository and
through the django-helpdesk documentation.

As you become comfortable with the system, its:

- source code;
- documentation;
- tests;
- issue history; and
- Git history

can all become useful sources of evidence when trying to understand why the system
behaves in a particular way.

The code under `student_demo/` is intended to make it easier to **enter and
experience** the system.

It is not a replacement for the django-helpdesk application itself.

---

# Your first objective

Before trying to change the application, make sure your group can explain:

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

Then choose **one behaviour or transition** in that flow and find the code
responsible for making it happen.

Do not begin with:

> Which files should I read?

Begin with:

> Why did the system behave this way?

That is where system comprehension begins.