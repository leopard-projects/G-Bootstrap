import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LinktestComponent } from './linktest.component';

describe('LinktestComponent', () => {
  let component: LinktestComponent;
  let fixture: ComponentFixture<LinktestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LinktestComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LinktestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
