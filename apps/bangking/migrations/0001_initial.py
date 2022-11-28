# Generated by Django 4.1.3 on 2022-11-28 21:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account_number', models.CharField(max_length=200)),
                ('balance', models.DecimalField(decimal_places=4, max_digits=19)),
            ],
            options={
                'db_table': 'accounts',
            },
        ),
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'account_types',
            },
        ),
        migrations.CreateModel(
            name='TransactionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('balance', models.DecimalField(decimal_places=4, max_digits=19)),
                ('is_withdrawal', models.BooleanField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('summary', models.CharField(max_length=50)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bangking.account')),
            ],
            options={
                'db_table': 'transaction_histories',
            },
        ),
        migrations.AddField(
            model_name='account',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bangking.accounttype'),
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.user'),
        ),
    ]
