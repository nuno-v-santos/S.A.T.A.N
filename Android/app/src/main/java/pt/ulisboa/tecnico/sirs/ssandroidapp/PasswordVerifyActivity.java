package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import java.util.Timer;
import java.util.TimerTask;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.SecurePreferences;

public class PasswordVerifyActivity extends AppCompatActivity { // Asks user a password and checks if it matches with the last inputed password

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_verify_password);
    }

    public void verifyPassword(View view) {
        EditText et = findViewById(R.id.passwordET);
        String password = et.getText().toString();

        SecurePreferences preferences =
                new SecurePreferences(this, Constants.PREFERENCES, password, true);

        if (password.trim().equals("")) {
            Toast.makeText(getApplicationContext(), R.string.invalid_empty_password, Toast.LENGTH_LONG).show();
            return;
        }

        // Let's try to get decypher a static test object and check if it matches with the original object
        String checkString = preferences.getString(Constants.PASSWORD_CHECK_STRING_ID);
        if (checkString == null || !checkString.equals(Constants.PASSWORD_CHECK_STRING)) { // since the id is also cyphered, if its unable to find the object id, its wrongly decyphered
            Toast.makeText(getApplicationContext(), R.string.incorrect_password, Toast.LENGTH_LONG).show();
            Button button = findViewById(R.id.passwordVerifySendButton);
            button.setEnabled(false);

            final Handler handler = new Handler() {
                @Override
                public void handleMessage(Message msg) {
                    Button button = findViewById(R.id.passwordVerifySendButton);
                    button.setEnabled(true);
                    super.handleMessage(msg);
                }
            };

            TimerTask task = new TimerTask() {
                @Override
                public void run() {
                    handler.sendEmptyMessage(0);
                }
            };
            new Timer().schedule(task, 1000); // disables button for 1000 milliseconds
            return;
        }

        Intent intent = new Intent(this, KeyExchangeActivity.class); // TODO connection activity

        intent.putExtra(Constants.PASSWORD_ID, password);
        startActivity(intent);
    }
}
