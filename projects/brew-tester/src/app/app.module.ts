import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { WBrewModule } from 'w-brew';
import { StoreModule } from '@ngrx/store';
import { promotionReducer } from './store/promotion/promotion.reducer';
import { Action } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { PromotionEffects } from './store/promotion/promotion.effects';
import { DemoComponent } from './components/demo/demo.component';
import { LinktestComponent } from './components/linktest/linktest.component';
import { CarouselEffect } from './store/carousel/carousel.effect';
import { carouselReducer } from './store/carousel/carousel.reducer';
import { PromotionhookComponent } from './components/promotionhook/promotionhook.component';

@NgModule({
  declarations: [
    AppComponent,
    DemoComponent,
    LinktestComponent,
    PromotionhookComponent
  ],
  imports: [
    BrowserModule,
    WBrewModule,
    HttpClientModule,
    AppRoutingModule,
    StoreModule.forRoot<unknown, Action>(
      {
        promotion: promotionReducer,
        carousel: carouselReducer
      }
    ),
    EffectsModule.forRoot([PromotionEffects, CarouselEffect])
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
