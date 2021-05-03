import { NgModule } from '@angular/core';
import { WBrewComponent } from './w-brew.component';
import { PromotionComponent } from './components/promotion/promotion.component';
import { ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { CarouselComponent } from './components/carousel/carousel.component';
import { NavigationComponent } from './components/navigation/navigation.component';
import { WideContainerComponent } from './components/wide-container/wide-container.component';
import { FullWideContainerComponent } from './components/full-wide-container/full-wide-container.component';
import { FooterComponent } from './components/footer/footer.component';
import { PagenotfoundComponent } from './components/pagenotfound/pagenotfound.component';
import { HorizontalCardComponent } from './components/horizontal-card/horizontal-card.component';
import { FullCardComponent } from './components/full-card/full-card.component';
import { NotificationComponent } from './components/notification/notification.component';



@NgModule({
  declarations: [
    WBrewComponent,
    PromotionComponent,
    CarouselComponent,
    NavigationComponent,
    WideContainerComponent,
    FullWideContainerComponent,
    FooterComponent,
    PagenotfoundComponent,
    HorizontalCardComponent,
    FullCardComponent,
    NotificationComponent
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
    FullWideContainerComponent,
    FooterComponent,
    PagenotfoundComponent,
    HorizontalCardComponent,
    FullCardComponent,
    NotificationComponent
  ]
})
export class WBrewModule { }
