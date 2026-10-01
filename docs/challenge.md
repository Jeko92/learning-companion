# Recap Project 6 - Agentic Engineering & AI Factory

Pick one framework you've never used before: **Django** (Python), **Spring Boot** (Java), or **Ruby on Rails** (Ruby).
Use your coding agent to research how this framework works and what technologies you want to use (database, frontend, testing, and so on).

## AI Factory Setup

Create a new repository and set up your AI factory pipeline. Your pipeline doesn't need to be perfect from the start.

- Set up a GitHub repository with a project board to track your tickets.
- Set up each pipeline stage with its SKILLS, RULES, and HOOKS.
- Set up a loop with a custom slash-command/prompt or skill to pick up the next ticket from the project board and invoke
  the Skill required for the next step.

## Ticket Setup

Create a ticket for each feature with a clear description of what you want to achieve.

- Installation of dependencies and project scaffolding.
- User authentication and profile management.
- CRUD for goals and learning sessions.
- Resource library for attaching reference material to goals.
- AI-powered summary and next steps for goals.
- Dashboard and reporting for goals and sessions.
- Containerization and CI/CD setup.

You will find more details about each feature in the following sections.

## Hints:

- Review and validate each output for each step of your pipeline.
- Improve each stage of your pipeline as soon as your review discovers any issues.
- Use TDD to implement each feature.
- Update the CLAUDE.md file with any new commands or architecture changes you make to your project.

## Learning Companion - Project setup

Get a runnable project before building any features.

- Install the required dependencies for the framework (Python + pip, Java + Maven/Gradle, or Ruby + Bundler).
- Scaffold a new project with the framework's own generator.

## Learning Companion - Authentication and profile management

Set up user authentication and profile management.

- Wire up the framework's built-in auth (Django auth, Spring Security starter, or Devise). This is where you see what an opinionated framework gives you out of the box.
- Add a `Profile` model/entity linked to the user with `name`, `cohort`, and a list of `focus_area` tags.
- Confirm you can sign up, log out, and log back in, and that the profile page only shows your own data.

## Learning Companion - Goals and sessions (CRUD + relationships)

Model the core domain and wire up full CRUD through the framework's ORM.

- Create a `Goal` entity: `title`, `description`, `status` (planned / in-progress / done), `created_at`, `updated_at`.
- Create a `LearningSession` entity linked to a `Goal`: `date`, `duration`, `notes`, and `tags`.
- Generate the migration with the framework's tooling (`makemigrations`/`migrate`, Flyway/Hibernate DDL, or
  `rails generate migration`).
- Build list, create, edit, and delete views/endpoints for both entities, scoped so a user only ever sees their own
  goals and sessions.
- Add filtering on the goals list by `status`.

## Learning Companion - Resource library

Attach reference material to a goal.

- Create a `Resource` entity: `url`, `title`, `type` (article / video / repo / doc), linked to a `Goal`.
- Add a form to attach a resource to a goal from the goal's detail page.
- Show the attached resources on the goal detail view, grouped or badged by `type`.

## Learning Companion - AI-powered summary and next steps

Re-use your OpenAI API/SDK knowledge, but call it from your new framework.

- Add a "Generate summary" action on the goal detail page that collects the goal's recent `LearningSession`s and
  `Resource`s, sends them to the OpenAI Chat Completions API, and displays the returned progress summary (e.g. "You
  spent 5 hours on Docker; you've covered X, next focus: Y").
- Add a "Suggest next steps" action that sends the goal plus its past sessions and asks for 2-3 concrete next learning
  actions; render the reply as a short list.
- Store your API key the idiomatic way for your framework (`.env` + `django-environ`, `application.properties` + env var
  injection, or Rails credentials/`dotenv`). Never hardcode it.

## Learning Companion - Dashboard and reporting

Use the ORM's aggregation features for these queries.

- Build a dashboard page showing the count of goals per `status`.
- Add a query that totals logged session hours per tag, and one that totals hours per week, using the framework's query
  builder/ORM aggregation (Django `annotate`/`aggregate`, JPQL/Criteria API, or ActiveRecord `group`/`sum`).
- Render both as simple tables or bars on the dashboard.

## Learning Companion - Containerize and add CI

Apply your DevOps week to an unfamiliar stack.

- Write a `Dockerfile` for the app using the framework's common base image and startup command, and confirm
  `docker build` + `docker run` serves the app.
- Add a CI workflow (GitHub Actions or similar) that installs dependencies and runs the framework's test runner on every
  push.
