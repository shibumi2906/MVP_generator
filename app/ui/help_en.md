### What you can do here
Describe your product in plain language. The generator prepares **draft requirements and
a development plan**: architecture, data model, API and tasks.
The working application and its source code still need to be built from that plan.

### 1. Describe your idea
Only **Product idea** is required, with at least 10 characters. For a useful result,
explain **who the user is → what problem they have → what they should be able to do**.
You can write in English or Russian. In OpenAI mode, the brief is sent to the model:
do not include passwords, API keys or real customer data.

| Field | What to enter | Example |
| --- | --- | --- |
| Product idea | The problem and 2–3 core features | A tutor manages students and lessons instead of using a notebook |
| Who is it for? | The intended audience | Independent tutors without an assistant |
| User workflow | User actions in order | Add a student → schedule a lesson → view the timetable |
| Constraints | Deadline, team size and exclusions | One developer, one week, no payments |
| Technologies | Preferred development tools | Keep the suggested stack if unsure |

Leave optional fields empty if you do not know the technical details.
**Fill in an example** replaces every field with a sample brief.
It does not start generation; you can edit it before submitting.

### 2. Click Generate development plan
Wait for the result below the form. In **OpenAI** mode, each run uses tokens.
In **Demo** mode, you get the same generic example, which is not adapted to your idea.
Successful results are saved automatically under **Saved plans** on the left.
Click a plan's title to reopen it without running another generation or using more tokens.

### 3. Review and download your documents
| Tab | What to check |
| --- | --- |
| Requirements | Whether the problem, audience and scope of the first release are correct |
| Architecture | The parts of the application and how they connect |
| Data model | Entities, fields and relationships, such as students and lessons |
| API | The requests the server should support; intended for developers |
| Delivery plan | Implementation order and checks for completion |
| Assumptions | What the model guessed and what you need to clarify |

Start with **Requirements** and **Assumptions**. If the idea was misunderstood,
edit your brief and generate a new plan. This is a separate request and uses tokens.
Structural checks verify references between documents; you still need to review
the product decisions yourself.

Click **Prepare ZIP**, then **Download documents**.
The archive contains Markdown text documents, Mermaid diagram sources and JSON data.
Share it with a developer or use it as the starting point for implementation.
It does not contain a working application.

### Tokens and the daily budget
Tokens are units of text the model reads and generates, not a count of requests.
The application allows **150,000 input + output tokens per day**, shared across
all generations here, resetting at **midnight Israel time**.
The sidebar counter includes usage and reservations for unfinished requests.
It survives server restarts. Requests from other applications and usage before
accounting was enabled are not included. If a failed request has no confirmed usage,
its reservation remains counted until the end of the day.

### If something goes wrong
- **Idea too short:** describe your product in at least 10 characters.
- **Request timed out:** no result was saved. Check saved plans and your token counter,
  simplify the brief and retry later. Another run may use more tokens.
- **Daily budget exhausted:** wait until midnight Israel time. Restarting does not reset it.
- **OpenAI rejected the request:** check the API key, model access and server settings.
- **OpenAI rate or quota limit:** check the balance and limits of your API account.
- **Document validation failed:** the model returned inconsistent documents.
  Limit the first release to a few core features and retry.
- **Server unavailable:** both the API and the interface need to be running.
  Keeping a browser window open is not enough; ask to start the application again.

A plan marked **Unknown origin** is a legacy result. You can open and download it,
but its source and document consistency have not been verified.
