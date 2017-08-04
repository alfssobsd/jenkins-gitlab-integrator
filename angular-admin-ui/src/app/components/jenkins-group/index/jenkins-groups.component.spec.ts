import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { JenkinsGroupsComponent } from './jenkins-groups.component';

describe('JenkinsGroupsComponent', () => {
  let component: JenkinsGroupsComponent;
  let fixture: ComponentFixture<JenkinsGroupsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ JenkinsGroupsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(JenkinsGroupsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });
});
