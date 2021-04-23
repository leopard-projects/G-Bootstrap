
import { Promotion } from 'w-brew';
import * as PromotionActions from './promotion.action';

export class State {
  promotion?: Promotion;
}

const promotionInit: Promotion = {};

const initState = {
  promotion: promotionInit
};

export function promotionReducer(state: State = initState, action: PromotionActions.PromotionActions) {
  switch (action?.type) {
    case PromotionActions.SET_PROMOTION:
      return {
        ...state,
        promotion: {
          ...action.payload
      }
    };
    case PromotionActions.FETCH_PROMOTION:
      return state;
    case PromotionActions.EDIT_PROMOTION:
      return state;
    default:
      return state;
  }
}
