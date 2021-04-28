import { Component, Input, OnInit } from '@angular/core';
import { CardModel } from '../../models/card.model';

@Component({
  selector: 'lib-full-card',
  templateUrl: './full-card.component.html',
  styleUrls: ['./full-card.component.scss']
})
export class FullCardComponent implements OnInit {
  @Input() card?: CardModel;
  constructor() { }

  ngOnInit(): void {
  }

}
