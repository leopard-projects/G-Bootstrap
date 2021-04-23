import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FullWideContainerComponent } from './full-wide-container.component';

describe('FullWideContainerComponent', () => {
  let component: FullWideContainerComponent;
  let fixture: ComponentFixture<FullWideContainerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FullWideContainerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FullWideContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
