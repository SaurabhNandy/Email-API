# Email-API
APIs to authorise, send and receive mail using Flask

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
 request body:
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
type can be plain or html depending on contents of the body
```

- Receive mail: host_url/mail-server/receive (POST)
```
request body:
{
	"sender_email": "",
	"password": "",
	"label": "",
	"count": "",
	"next_mail_id": ""
}
- count is an integer which defines number of mails to be fetched
- next_mail_id is an integer, null when next_mail_id is not known
```
