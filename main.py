# ... (previous imports remain the same)

@app.route('/onboard/<user_type>', methods=['GET', 'POST'])
@login_required
def onboard(user_type):
    if user_type not in ['buyer', 'seller', 'vendor']:
        flash('Invalid user type.', 'error')
        return redirect(url_for('index'))
    
    form = OnboardingForm()
    if form.validate_on_submit():
        current_user.experience = form.experience.data
        current_user.interests = form.interests.data
        current_user.location = form.location.data
        current_user.garden_size = form.garden_size.data
        current_user.soil_type = form.soil_type.data
        current_user.sunlight = form.sunlight.data
        current_user.watering_frequency = form.watering_frequency.data
        current_user.preferred_products = form.preferred_products.data
        current_user.organic_preference = form.organic_preference.data
        current_user.climate_zone = form.climate_zone.data
        current_user.goals = form.goals.data
        current_user.challenges = form.challenges.data
        
        # Calculate onboarding progress
        filled_fields = sum(1 for f in form if f.data and f.name != 'csrf_token')
        total_fields = len([f for f in form if f.name != 'csrf_token'])
        current_user.onboarding_progress = int((filled_fields / total_fields) * 100)
        
        if current_user.onboarding_progress == 100:
            current_user.onboarding_complete = True
            flash('Onboarding completed successfully!', 'success')
        else:
            flash(f'Onboarding {current_user.onboarding_progress}% complete. Please fill out more information to get personalized recommendations.', 'info')
        
        db.session.commit()
        
        # Suggest products based on user's location and climate zone
        suggested_products = get_product_recommendations(current_user)
        
        return render_template('onboarding_results.html', 
                               user=current_user, 
                               progress=current_user.onboarding_progress, 
                               suggested_products=suggested_products)
    
    return render_template('onboarding.html', form=form, user_type=user_type, progress=current_user.onboarding_progress)

# ... (rest of the file remains the same)
