import * as CarouselActions from './carousel.action';
import { Carousel } from 'w-brew';

export class CarouselState {
  slides?: Carousel[];
}

const carouselInit: Carousel[] = <Carousel[]>[];

const initState: CarouselState = {
  slides: carouselInit,
};

export function carouselReducer(
  state: CarouselState = initState,
  action: CarouselActions.CarouselActions
) {
  switch (action?.type) {
    case CarouselActions.FETCH_CAROUSEL:
      return state;
    case CarouselActions.SET_CAROUSEL:
      return {
        ...state,
        slides: [...action.payload]
      };
    default:
      return state;
  }
}
