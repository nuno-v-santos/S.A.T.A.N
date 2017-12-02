package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.SecurePreferences;

public class PasswordRequestActivity extends AppCompatActivity { // Request user a password for the first time

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_request_password);
    }

    public void sendPassword(View view) {
        EditText et = findViewById(R.id.passwordET);
        String password = et.getText().toString();

        if (password.trim().equals("")) {
            Toast.makeText(getApplicationContext(), R.string.invalid_empty_password, Toast.LENGTH_LONG).show();
            return;
        }

        SecurePreferences preferences =
                new SecurePreferences(this, Constants.PREFERENCES, password, true);

        preferences.put(Constants.PASSWORD_CHECK_STRING_ID, Constants.PASSWORD_CHECK_STRING); // used later to verify if inputed password is correct

        Intent intent = new Intent(this, BluetoothActivity.class);

        intent.putExtra(Constants.PASSWORD_ID, password); // password is carried over through the activity chains
        startActivity(intent);
    }
}
