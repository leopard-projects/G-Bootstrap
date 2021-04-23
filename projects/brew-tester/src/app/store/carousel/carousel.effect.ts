import { Injectable } from '@angular/core';
import { Actions, Effect, ofType } from '@ngrx/effects';
import * as CarouselActions from './carousel.action';
import { switchMap, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Carousel } from 'w-brew';

@Injectable()
export class CarouselEffect {

  constructor(
    private actions$: Actions,
    private http: HttpClient
  ) {}

@Effect()
fetchCarouset = this.actions$.pipe(
  ofType(CarouselActions.FETCH_CAROUSEL),
  switchMap(() => {
    const carouselUrl = environment.api.carousel;
    return this.http.get<Carousel[]>(carouselUrl);
  }),
  map((carouselData: Carousel[]) => {
    if ( carouselData && carouselData.length > 0 ) {
      return carouselData;
    }
    else {
      return <Carousel[]>[];
    }
  }),
  map((carouselData: Carousel[]) => {
    return new CarouselActions.SetCarousel(carouselData);
  })
)

}
