from src.flurry.systems.web import FlurryWeb
from src.flurry.systems.user import FlurryUser
import flurryflake.filters.camflow as camflow

test1 = FlurryWeb(camflow.W3CFilter())
test2 = FlurryUser(camflow.W3CFilter())
