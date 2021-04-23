import { Component, Input, OnInit } from '@angular/core';
import { WideContainerModel } from '../../models/wide.container.model';

@Component({
  selector: 'lib-wide-container',
  templateUrl: './wide-container.component.html',
  styleUrls: ['./wide-container.component.scss']
})
export class WideContainerComponent implements OnInit {
  @Input() widedata?: WideContainerModel
  constructor() { }

  ngOnInit(): void {
  }
}
