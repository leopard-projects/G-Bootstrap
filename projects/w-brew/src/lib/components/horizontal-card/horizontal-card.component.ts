import { Component, Input, OnInit } from '@angular/core';
import { CardModel } from '../../models/card.model';

@Component({
  selector: 'lib-horizontal-card',
  templateUrl: './horizontal-card.component.html',
  styleUrls: ['./horizontal-card.component.scss']
})
export class HorizontalCardComponent implements OnInit {
  @Input() content?: CardModel;

  constructor() { }

  ngOnInit(): void {
  }
}
