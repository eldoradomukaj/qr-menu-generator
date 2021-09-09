## NoMenu - QR Code Menu Builder

NoMenu is a simple to use restaurant menu builder that generates a QR code for easy linking to your menu.

### Requirements

- A Postgresql databse
- AWS S3 bucket

### Usage

Under settings.py:

- Create a secret key (any string will work)
- add your postgresql connection info
- Add your AWS S3 bucket name, and API key
- Add a SMTP server

#### To Do

- Add dockerfile
