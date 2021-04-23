import { Component, Input, OnInit } from '@angular/core';
import { Carousel } from '../../models/carousel.model';

@Component({
  selector: 'lib-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.scss']
})
export class CarouselComponent implements OnInit {
  @Input() slides?: Carousel[]
  constructor() { }

  ngOnInit(): void {
  }

}
