import { Component, Input, OnInit } from '@angular/core';
import { FullWideModel } from '../../models/full-wide.model';

@Component({
  selector: 'lib-full-wide-container',
  templateUrl: './full-wide-container.component.html',
  styleUrls: ['./full-wide-container.component.scss']
})
export class FullWideContainerComponent implements OnInit {
  @Input() fullWideContent?: FullWideModel;
  constructor() { }

  ngOnInit(): void {
  }

}
