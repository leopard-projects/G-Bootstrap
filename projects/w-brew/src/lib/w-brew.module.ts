import { NgModule } from '@angular/core';
import { WBrewComponent } from './w-brew.component';
import { PromotionComponent } from './components/promotion/promotion.component';
import { ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { CarouselComponent } from './components/carousel/carousel.component';
import { NavigationComponent } from './components/navigation/navigation.component';
import { WideContainerComponent } from './components/wide-container/wide-container.component';
import { FullWideContainerComponent } from './components/full-wide-container/full-wide-container.component';



@NgModule({
  declarations: [
    WBrewComponent,
    PromotionComponent,
    CarouselComponent,
    NavigationComponent,
    WideContainerComponent,
    FullWideContainerComponent
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule
  ],
  exports: [
    WBrewComponent,
    PromotionComponent,
    CarouselComponent,
    NavigationComponent,
    WideContainerComponent,
    FullWideContainerComponent
  ]
})
export class WBrewModule { }
