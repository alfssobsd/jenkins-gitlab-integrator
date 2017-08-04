import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { JenkinsGroupEditComponent } from './jenkins-group-edit.component';

describe('JenkinsGroupEditComponent', () => {
  let component: JenkinsGroupEditComponent;
  let fixture: ComponentFixture<JenkinsGroupEditComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ JenkinsGroupEditComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(JenkinsGroupEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
