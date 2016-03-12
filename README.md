# Hacker's Outreach

Hacker's Outreach is a simple email outreach automation for command line lovers.

First, save an email template in `template.txt` (the first line is the subject):

```
I saw you're looking for engineers!
Hey {name}!

{intro}

I saw you're looking for engineers. I'm available for hire. Just let me know
when I can start!

Best regards
```

Second, prepare `outreach.yml` campaign file:

```
name: Job Outreach
from: 'John Unemployed <john.unemployed@gmail.com>'
template: template.txt
targets:
  - to: ceo@company1.com
    name: Adam
    intro: I always wanted to work for aerospace!
  - to: cto@company2.com
    name: Thomas
    intro: Congrats on your TechCrunch story!
```

Now just run:

```
./outreach send outreach.yml
```

That's it! You can add more targets to `outreach.yml` and rerun the campaign.
People who were contacted during the first run will _not_ be contacted again.

## Installation

0. Install Python 2.7 and `virtualenvwrapper`.
1. Clone the repo `git clone https://github.com/gregnavis/hackout`.
2. Enter the repo: `cd hackout`.
3. Create a virtual environment: `mkvirtualenv hackout`.
3. Install the dependencies: `pip install -r requirements.txt`.
4. Run `./outreach authn` and complete the GMail authentication procedure.

## Rules

1. The first line of the template is the subject line.
2. Each email sent in a campaign is labeled with a campaign-specific label.
3. Each campaign can send only one email to a given address. This is to ensure
   that each 

## Upcoming Featuers

* Follow-up emails.
* Open rate tracking.
* A/B testing.
* Sending at a given time in the recipient's timezone.
* Spreadsheet import.
