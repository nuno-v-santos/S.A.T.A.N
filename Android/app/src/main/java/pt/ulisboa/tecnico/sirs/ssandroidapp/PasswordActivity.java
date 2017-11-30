package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

public class PasswordActivity extends AppCompatActivity { // User always introduces the correct password
    String nextClassName;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_password);
        nextClassName = getIntent().getStringExtra(Constants.NEXT_CLASS_ID);
    }

    public void sendPassword(View view) {
        try {
            EditText et = findViewById(R.id.passwordET);
            String password = et.getText().toString();
            if (password.trim().equals("")) {
                Toast.makeText(getApplicationContext(), R.string.invalid_password, Toast.LENGTH_LONG).show();
                return;
            }

            Class<?> nextActivity = Class.forName(nextClassName);
            Intent intent = new Intent(this, nextActivity);

            intent.putExtra(Constants.PASSWORD_ID, password);
            startActivity(intent);
        } catch (ClassNotFoundException cne) {
            cne.printStackTrace();
        }
    }
}
