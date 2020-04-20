# Email-API
APIs to authorise, send and receive mail in python

## Available Api Endpoints
- Authorise user: host_url/mail-server/authenticate (POST)
```
request body:
{
	"sender_email": "",
	"password": ""
}
```

- Send a mail: host_url/mail-server/send (POST)
 ```
{
	"sender_email": "",
	"password": "",
	"receiver_email": "",
	"subject": "",
	"body": {
		"type": "",
		"content": ""
	}
}
```

- Receive mail: host_url/mail-server/receive (POST)
```
{
	"sender_email": "",
	"password": "",
	"label": "",
	"count": "",
	"next_mail_id": ""
}
```
