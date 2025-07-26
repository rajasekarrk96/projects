from migrations.add_is_read_to_message import upgrade

if __name__ == '__main__':
    upgrade()
    print("Migration completed successfully!") 