import os
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.admin.schemas import InstrumentCreateRequest, BalanceChangeScheme
from app.api.v1.auth.jwt import get_current_admin
from app.crud.instrument import create_instrument, get_instrument_by_ticker, delete_instrument
from app.crud.user import get_user, change_balance, delete_user
from app.database.models import User, Instrument
from app.depends import get_instrument_depend, get_user_depend

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post('/instrument', status_code=status.HTTP_201_CREATED)
async def create_new_instrument(payload: InstrumentCreateRequest, admin: User = Depends(get_current_admin)):
    existing = await get_instrument_by_ticker(payload.ticker)
    if existing:
        raise HTTPException(status_code=422, detail="Instrument already exists")
    await create_instrument(payload.name, payload.ticker)
    return {"success": True}


@router.post('/balance/deposit')
async def deposit_funds(payload: BalanceChangeScheme, admin: User = Depends(get_current_admin)):
    user = await get_user(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await change_balance(payload.user_id, payload.ticker, payload.amount)
    return {"success": True}


@router.post('/balance/withdraw')
async def withdraw_funds(payload: BalanceChangeScheme, admin: User = Depends(get_current_admin)):
    user = await get_user(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await change_balance(payload.user_id, payload.ticker, -payload.amount)
    return {"success": True}


@router.delete('/user/{user_id}')
async def remove_user(user_to_delete: User = Depends(get_user_depend), admin: User = Depends(get_current_admin)):
    deleted = await delete_user(user_to_delete.id)
    return {"id": deleted.id, "name": deleted.name, "role": deleted.role.value, "api_key": deleted.api_key}


@router.delete('/instrument/{ticker}')
async def remove_instrument(instrument: Instrument = Depends(get_instrument_depend), admin: User = Depends(get_current_admin)):
    await delete_instrument(instrument.ticker)
    return {"success": True}
