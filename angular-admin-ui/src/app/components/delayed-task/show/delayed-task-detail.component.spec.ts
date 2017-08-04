import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DelayedTaskDetailComponent } from './delayed-task-detail.component';

describe('DelayedTaskDetailComponent', () => {
  let component: DelayedTaskDetailComponent;
  let fixture: ComponentFixture<DelayedTaskDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DelayedTaskDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DelayedTaskDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
