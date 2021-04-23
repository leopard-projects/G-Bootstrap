import { Actions, Effect, ofType } from '@ngrx/effects';
import * as PromotionActions from './promotion.action';
import { switchMap, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Promotion } from 'w-brew';
import { Injectable } from '@angular/core';

@Injectable()
export class PromotionEffects {
  constructor(
    private actions$: Actions,
    private http: HttpClient
  ) {}

  @Effect()
  fetchPromotion = this.actions$.pipe(
    ofType(PromotionActions.FETCH_PROMOTION),
    switchMap(() => {
      const promotionUrl = environment.api.promotion;
      return this.http.get<Promotion>(promotionUrl);
    }),
    map((promotionData) => {
      return {
        ...promotionData,
        promotion: promotionData ? promotionData : {}
      };
    }),
    map(promotion => {
      return new PromotionActions.SetPromotion(promotion);
    })
  );
}
