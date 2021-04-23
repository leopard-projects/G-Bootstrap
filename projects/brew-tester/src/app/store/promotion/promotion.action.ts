import { Action } from '@ngrx/store';
import { Promotion } from 'w-brew';

export const EDIT_PROMOTION = '[Promotion] Edit Promotion';
export const FETCH_PROMOTION = '[Promotion] Fetch Promotion';
export const SET_PROMOTION = '[Promotion] Set Promotion';

export class EditPromotion implements Action {
  readonly type = EDIT_PROMOTION;

  constructor(public payload: {promotion: Promotion}) {}
}

export class FetchPromotion implements Action {
  readonly type = FETCH_PROMOTION;
}

export class SetPromotion implements Action {
  readonly type = SET_PROMOTION;

  constructor(public payload: Promotion) {
  }
}

export type PromotionActions =
  | EditPromotion
  | FetchPromotion
  | SetPromotion;
