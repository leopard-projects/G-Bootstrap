import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';

import {
  Carousel,
  Promotion
} from 'w-brew';

import * as PromotionActions from '../../store/promotion/promotion.action';

@Component({
  selector: 'app-promotionhook',
  templateUrl: './promotionhook.component.html',
  styleUrls: ['./promotionhook.component.scss']
})
export class PromotionhookComponent implements OnInit {

  promotionData?: Observable<{ promotion: Promotion }>;
  promotion?: Promotion;

  constructor(
    private store: Store<{
      promotion: {promotion: Promotion},
      carousel: {slides: Carousel[]}
    }>
  ) { }

  ngOnInit(): void {
    this.store.select('promotion').subscribe( (data: { promotion: Promotion }) => {
      this.promotion = data.promotion;
      if ( this.promotion
        && Object.keys(this.promotion).length === 0
        && this.promotion.constructor === Object ) {
          this.promotion = undefined;
          this.store.dispatch(new PromotionActions.FetchPromotion());
      }
    });
  }

  promotionReverse(event:any) {
    const promotionData: Promotion = event;
    this.store.dispatch(new PromotionActions.SetPromotion(promotionData));
  }
}
