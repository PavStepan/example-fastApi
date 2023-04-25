import json
import uvicorn
from starlette.exceptions import HTTPException
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from starlette.responses import JSONResponse
from yookassa import Refund
from yookassa.domain.exceptions import BadRequestError
from database import get_status_payment, add_refund, get_price
from config import api_config, domain_config

app = FastAPI()
security = HTTPBearer()

REFUNDS = []


class RefundItem(BaseModel):
    user_id: str
    amount: str
    payment_id: str
    description: str = ""


@app.on_event("startup")
@repeat_every(seconds=5)
async def refund_webhook():
    for entry in REFUNDS:
        refund_id = entry['payment_id']
        refund = json.loads((Refund.find_one(refund_id)).json())

        if refund['status'] == 'pending':
            print("STATUS PENDING")
        elif refund['status'] == 'succeeded':
            print("SUCCESS RETURN")
            print(entry)
            add_refund(entry)
            refund.remove(entry)
        elif refund['status'] == 'canceled':
            print("STATUS canceled")
        else:
            print("BAD RETURN")
            print(refund)


@app.post("/refund")
async def refund_function(item: RefundItem, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token != API_TOKEN:
        raise HTTPException(status_code=401)
    if item.amount.isnumeric():
        raise HTTPException(status_code=500, detail="bad amount")

    refund_amount = "{:.2f}".format(float(item.amount))
    status = get_status_payment(item.user_id, item.payment_id)
    if status != 'refund':
        refund_one = ({"user_id": item.user_id,
                       "payment_id": item.payment_id,
                       "refundAmount": float(item.amount),
                       'description': item.description})
        try:
            refund = Refund.create({
                "amount": {
                    "value": refund_amount,
                    "currency": "RUB"},
                'payment_id': item.payment_id,
                'description': item.description})
            REFUNDS.append(refund_one)
        except BadRequestError as error_refund:
            error_msg = error_refund.args[0]['description']
            if error_msg == 'Payment is already completely refunded. You can not return it.':
                add_refund(refund_one)
            refund = {'error': error_msg}
        return refund


@app.get("/prices")
def prices(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token != API_TOKEN:
        raise HTTPException(status_code=401)
    data = dict()
    tariff = get_price()
    for tariff_info in tariff:
        row = {tariff_info[0]: [tariff_info[1], tariff_info[2]]}
        data.update(row)
    return JSONResponse(content=data)


if __name__ == '__main__':
    API_TOKEN = api_config()
    host, port = domain_config()
    uvicorn.run(app, host='0.0.0.0', port=8000)
