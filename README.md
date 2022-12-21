# Sale_Snearkers_bot

![Запись экрана 2022-11-23 в 12 53 39](https://user-images.githubusercontent.com/114915003/203508159-484225ec-026d-4688-b287-483dc2feca7a.gif)

## How to use?

Use the [pip](https://pip.pypa.io/en/stable/) package manager to install dependencies for the project

## bot.polling() or set_webhook

You can use both methods for the bot to work, I recommend set_webhook for deployment, and if you want to run it locally on your computer, you can do bot.polling()
You can read more about set_webhooks and bot.polling [here](https://core.telegram.org)

### set_webhook:

```python
@server.route(f"/{TG_TOKEN}", methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return "!", 200


if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
```

### bot.polling():

```python
if __name__ == '__main__':
   bot.polling()
```

You need to create your own config.py the file in which the secret of the moon will be TG_TOKEN, CONNECTION_STRING(for MongoDB)

You also need to install dependencies:

```bash
pip install -r requirements.txt
```


## How to use Mongo DB?

[Docs](https://www.mongodb.com/docs/) Mongo DB







