from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="RuleSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("version", models.CharField(default="v1", max_length=50)),
                ("technical_rules", models.JSONField(default=dict)),
                ("medical_rules", models.JSONField(default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rule_sets", to="engine.tenant")),
            ],
            options={"unique_together": ("tenant", "name", "version")},
        ),
        migrations.CreateModel(
            name="Claim",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("claim_id", models.CharField(max_length=64)),
                ("encounter_type", models.CharField(blank=True, max_length=64, null=True)),
                ("service_date", models.DateField(blank=True, null=True)),
                ("national_id", models.CharField(blank=True, max_length=64, null=True)),
                ("member_id", models.CharField(blank=True, max_length=64, null=True)),
                ("facility_id", models.CharField(blank=True, max_length=64, null=True)),
                ("unique_id", models.CharField(blank=True, max_length=64, null=True)),
                ("diagnosis_codes", models.JSONField(default=list)),
                ("service_code", models.CharField(blank=True, max_length=64, null=True)),
                ("paid_amount_aed", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("approval_number", models.CharField(blank=True, max_length=128, null=True)),
                ("status", models.CharField(default="Uploaded", max_length=32)),
                ("error_type", models.CharField(default="No error", max_length=64)),
                ("error_explanation", models.TextField(blank=True, default="")),
                ("recommended_action", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="claims", to="engine.tenant")),
            ],
            options={"indexes": [models.Index(fields=["tenant", "claim_id"], name="engine_clai_tenant__2c3256_idx"), models.Index(fields=["tenant", "status"], name="engine_clai_tenant__b62902_idx")]},
        ),
        migrations.CreateModel(
            name="RefinedClaim",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_valid", models.BooleanField(default=False)),
                ("tech_errors", models.JSONField(default=list)),
                ("med_errors", models.JSONField(default=list)),
                ("llm_findings", models.JSONField(default=list)),
                ("score", models.FloatField(default=0)),
                ("claim", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="refined", to="engine.claim")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="engine.tenant")),
            ],
        ),
        migrations.CreateModel(
            name="Metric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("as_of", models.DateTimeField(auto_now_add=True)),
                ("counts_by_error", models.JSONField(default=dict)),
                ("paid_by_error", models.JSONField(default=dict)),
                ("rule_set", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="engine.ruleset")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="engine.tenant")),
            ],
        ),
        migrations.CreateModel(
            name="JobRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("job_type", models.CharField(max_length=64)),
                ("status", models.CharField(default="Pending", max_length=32)),
                ("detail", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("rule_set", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="engine.ruleset")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="engine.tenant")),
            ],
        ),
    ]
# Generated by Django 5.2.6 on 2025-09-19 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('claim_id', models.CharField(max_length=64)),
                ('encounter_type', models.CharField(blank=True, max_length=64, null=True)),
                ('service_date', models.DateField(blank=True, null=True)),
                ('national_id', models.CharField(blank=True, max_length=64, null=True)),
                ('member_id', models.CharField(blank=True, max_length=64, null=True)),
                ('facility_id', models.CharField(blank=True, max_length=64, null=True)),
                ('unique_id', models.CharField(blank=True, max_length=64, null=True)),
                ('diagnosis_codes', models.JSONField(default=list)),
                ('service_code', models.CharField(blank=True, max_length=64, null=True)),
                ('paid_amount_aed', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('approval_number', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.CharField(default='Uploaded', max_length=32)),
                ('error_type', models.CharField(default='No error', max_length=64)),
                ('error_explanation', models.TextField(blank=True, default='')),
                ('recommended_action', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='RuleSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(default='v1', max_length=50)),
                ('technical_rules', models.JSONField(default=dict)),
                ('medical_rules', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rule_sets', to='engine.tenant')),
            ],
            options={
                'unique_together': {('tenant', 'name', 'version')},
            },
        ),
        migrations.CreateModel(
            name='RefinedClaim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_valid', models.BooleanField(default=False)),
                ('tech_errors', models.JSONField(default=list)),
                ('med_errors', models.JSONField(default=list)),
                ('llm_findings', models.JSONField(default=list)),
                ('score', models.FloatField(default=0)),
                ('claim', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='refined', to='engine.claim')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engine.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('as_of', models.DateTimeField(auto_now_add=True)),
                ('counts_by_error', models.JSONField(default=dict)),
                ('paid_by_error', models.JSONField(default=dict)),
                ('rule_set', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='engine.ruleset')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engine.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='JobRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_type', models.CharField(max_length=64)),
                ('status', models.CharField(default='Pending', max_length=32)),
                ('detail', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('rule_set', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='engine.ruleset')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engine.tenant')),
            ],
        ),
        migrations.AddField(
            model_name='claim',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claims', to='engine.tenant'),
        ),
        migrations.AddIndex(
            model_name='claim',
            index=models.Index(fields=['tenant', 'claim_id'], name='engine_clai_tenant__a04c87_idx'),
        ),
        migrations.AddIndex(
            model_name='claim',
            index=models.Index(fields=['tenant', 'status'], name='engine_clai_tenant__a15a38_idx'),
        ),
    ]
