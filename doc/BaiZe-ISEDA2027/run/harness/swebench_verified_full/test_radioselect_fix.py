from django.db import models
from django.forms import ModelForm, RadioSelect
from django.test import TestCase


class BatchData(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TestRun(models.Model):
    data_file = models.ForeignKey(BatchData, on_delete=models.SET_NULL, null=True, blank=False)


class TestRunForm(ModelForm):
    class Meta:
        model = TestRun
        fields = ['data_file']
        widgets = {'data_file': RadioSelect()}


class RadioSelectEmptyOptionTest(TestCase):
    def test_radioselect_no_empty_option_when_blank_false(self):
        # Create test data
        BatchData.objects.create(name="First Data File")
        BatchData.objects.create(name="Second Data File")
        
        # Instantiate form
        form = TestRunForm()
        
        # Render the field
        rendered = str(form['data_file'])
        
        # Check that there's no empty option
        self.assertNotIn('value=""', rendered)
        self.assertNotIn('---------', rendered)
        
        # Check that both options are present
        self.assertIn('First Data File', rendered)
        self.assertIn('Second Data File', rendered)
        
        # Check that no option is checked by default
        self.assertNotIn('checked="checked"', rendered)
        
    def test_radioselect_empty_option_when_blank_true(self):
        # Test model with blank=True
        class TestRunBlank(models.Model):
            data_file = models.ForeignKey(BatchData, on_delete=models.SET_NULL, null=True, blank=True)
            
        class TestRunBlankForm(ModelForm):
            class Meta:
                model = TestRunBlank
                fields = ['data_file']
                widgets = {'data_file': RadioSelect()}
                
        form = TestRunBlankForm()
        rendered = str(form['data_file'])
        
        # Empty option should be present
        self.assertIn('value=""', rendered)
        self.assertIn('---------', rendered)
        
    def test_select_widget_still_has_empty_option(self):
        # Test that regular Select widget still has empty option for required fields
        class TestRunSelectForm(ModelForm):
            class Meta:
                model = TestRun
                fields = ['data_file']
                
        form = TestRunSelectForm()
        rendered = str(form['data_file'])
        
        # Empty option should be present for Select widget
        self.assertIn('value=""', rendered)
        self.assertIn('---------', rendered)
