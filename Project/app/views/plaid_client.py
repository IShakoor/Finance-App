from plaid.api import plaid_api
import plaid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
import json
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api_client import ApiClient


# initialise plaid client
def get_plaid_client():
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            "clientId": settings.PLAID_CLIENT_ID,
            "secret": settings.PLAID_SECRET,
        },
    )
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


# create link token
@require_GET
def create_link_token(request):
    plaid_client = get_plaid_client()
    request_data = LinkTokenCreateRequest(
        user={"client_user_id": str(request.user.id if request.user.is_authenticated else "guest_user")},
        client_name="Finance App",
        products=[Products("auth"), Products("transactions")],
        country_codes=[CountryCode("GB")],
        language="en",
    )
    response = plaid_client.link_token_create(request_data)
    return JsonResponse({"link_token": response.link_token})


# exchange public token for access token
@csrf_exempt
@require_POST
@login_required
def exchange_public_token(request):
    plaid_client = get_plaid_client()
    try:
        data = json.loads(request.body)
        public_token = data.get("public_token")
        if not public_token:
            return JsonResponse({"success": False, "error": "Public token is missing."}, status=400)

        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = plaid_client.item_public_token_exchange(exchange_request)
        access_token = exchange_response.access_token

        if not access_token:
            return JsonResponse({"success": False, "error": "Access token not received."}, status=400)

        if request.user.is_authenticated:
            request.user.plaid_access_token = access_token
            request.user.save()
            return JsonResponse({"success": True, "message": "Access token saved successfully!"})
        else:
            return JsonResponse({"success": False, "error": "User is not authenticated."}, status=401)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
