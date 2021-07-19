import { Directive, ElementRef, HostListener, Input } from "@angular/core";

@Directive({
  selector: "[libNumberordecimals]",
})
export class NumberordecimalsDirective {
  // private regex: RegExp = new RegExp(/^\d*\.?\d{0,2}$/g);
  // private regex?: RegExp;
  private specialKeys: Array<string> = [
    "Backspace",
    "Tab",
    "End",
    "Home",
    "-",
    "ArrowLeft",
    "ArrowRight",
    "Del",
    "Delete",
  ];

  @Input("libNumberordecimals") regexPattern?: RegExp;

  constructor(private el: ElementRef) {}

  @HostListener("keydown", ["$event"])
  onKeyDown(event: KeyboardEvent) {
    // this.regex = this.params;
    console.log(this.el.nativeElement.value);
    // Allow Backspace, tab, end, and home keys
    if (this.specialKeys.indexOf(event.key) !== -1) {
      return;
    }
    let current: string = this.el.nativeElement.value;
    const position = this.el.nativeElement.selectionStart;
    const next: string = [
      current.slice(0, position),
      event.key == "Decimal" ? "." : event.key,
      current.slice(position),
    ].join("");
    if (next && this.regexPattern && !String(next).match(this.regexPattern)) {
      event.preventDefault();
    }
  }
}
