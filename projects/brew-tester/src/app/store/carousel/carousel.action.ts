import { Action } from '@ngrx/store';
import { Carousel } from 'w-brew';

export const FETCH_CAROUSEL = '[CAROUSEL] Fetch Carousel';
export const SET_CAROUSEL = '[CAROUSEL] Set Carousel';

export class FetchCarousel implements Action {
  readonly type = FETCH_CAROUSEL;
}

export class SetCarousel implements Action {
  readonly type = SET_CAROUSEL;

  constructor(public payload: Carousel[]) {}
}

export type CarouselActions =
  | FetchCarousel
  | SetCarousel;



