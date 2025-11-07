import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateRatingPage } from './create-rating-page';

describe('CreateRatingPage', () => {
  let component: CreateRatingPage;
  let fixture: ComponentFixture<CreateRatingPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateRatingPage]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateRatingPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
