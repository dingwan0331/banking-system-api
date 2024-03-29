# Generated by Django 4.1.3 on 2022-11-30 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('balance', models.DecimalField(decimal_places=4, max_digits=19)),
                ('is_withdrawal', models.BooleanField()),
                ('time', models.PositiveIntegerField()),
                ('date', models.PositiveIntegerField()),
                ('summary', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'transactions',
            },
        ),
        migrations.AddField(
            model_name='account',
            name='password',
            field=models.BinaryField(default=b'', max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='account_number',
            field=models.BinaryField(max_length=256),
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
        migrations.AddField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transaction.account'),
        ),
    ]
