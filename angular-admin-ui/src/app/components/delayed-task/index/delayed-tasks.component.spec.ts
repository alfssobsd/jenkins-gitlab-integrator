import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DelayedTasksComponent } from './delayed-tasks.component';

describe('DelayedTasksComponent', () => {
  let component: DelayedTasksComponent;
  let fixture: ComponentFixture<DelayedTasksComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DelayedTasksComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DelayedTasksComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
