import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import { LinkModel } from "../../models/link.model";
import { NavigationModel } from "../../models/navigation.model";

@Component({
  selector: "lib-navigation",
  templateUrl: "./navigation.component.html",
  styleUrls: ["./navigation.component.scss"],
})
export class NavigationComponent implements OnInit {
  @Input() navigationStructure?: NavigationModel;
  @Output() navigationTriggerred: EventEmitter<LinkModel> =
    new EventEmitter<LinkModel>();
  constructor() {}

  ngOnInit(): void {}

  triggerred(link: LinkModel) {
    // console.log(link);
    this.navigationTriggerred.emit(link);
  }
}
