## COVID-19 WhatsApp Bot  🇮🇳

A WhatsApp bot to track COVID-19 cases in India, powered by Twilio.

### Motivation

There is an ocean of information about COVID-19 on the Internet, but WhatsApp still remains the primary source for a vast majority of people. We provide clutter-free information to help you stay informed of COVID-19 cases around you, and be prepared for any eventuality.

### Features

- **Get country and state-wide statistics**.
  * Cumulative total, active, and new cases since last update.
  * Number of patients confirmed, recovered, and deceased.
- **Share your WhatsApp location**.
  * Get localized statistics on the number of cases.
  * Get distance from the closest detected active case.
- **Find essential services around you**.
  * COVID-19 testing labs.
  * Emergency healthcare services.
  * Free food.
  * Mental well-being and emotional support.
  * Delivery services (vegetables, fruits, groceries, medicines).
  * Government / NGO helplines.
  
### Wishlist

- Easy to understand graphical representation of COVID-19 statistics, delivered as images.
- Push notifications for important updates.
- Curate essential services from multiple sources.
- Send health advisories from local agencies.

### Local development

Make sure you have Python 3.8 and [Pipenv](https://github.com/pypa/pipenv) installed on your machine.

```sh
$ pipenv install --dev
$ pipenv run devserver
```


### Tech Stack

- [Twilio API for WhatsApp](https://www.twilio.com/whatsapp)
- [Flask](https://flask.palletsprojects.com) microservice framework / Python 3.8
- [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org)

### WhatsApp Bot Screens

#### Country and State-wide Statistics

<p align="center">
  <img src="/assets/total.jpeg" width="300px">
  <img src="/assets/maharashtra.jpeg" width="300px">
</p>

#### Localized cases

<p align="center">
  <img src="/assets/location.jpeg" width="300px">
  <img src="/assets/local_cases.jpeg" width="300px">
</p>

#### Essential Services

<p align="center">
  <img src="/assets/mental_health.jpeg" width="210px">
  <img src="/assets/other_essentials.jpeg" width="210px">
  <img src="/assets/govt_helplines.jpeg" width="210px">
  <img src="/assets/delivery.jpeg" width="210px">
</p>
