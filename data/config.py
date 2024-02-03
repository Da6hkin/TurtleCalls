from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")

ADMINS = env.list("ADMINS")

DSN = env.str("DSN")

ALLOWED_GROUPS = env.list("ALLOWED_GROUPS")

CHANNEL_ID = env.str("CHANNEL_ID")
